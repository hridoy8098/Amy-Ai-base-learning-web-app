from datetime import date, datetime, timedelta
import json
import re

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import and_, func
from sqlalchemy.orm import Session
from typing import List, Optional

from core.ai_providers import call_ai
from core.config import QUIZ_LIMITS
from core.database import get_db
from core.security import get_current_user
from models.models import QuizResult, User

router = APIRouter()

LANGUAGE_LABELS = {
    "en": "English",
    "bn": "Bangla",
    "hi": "Hindi",
    "ur": "Urdu",
    "ar": "Arabic",
    "zh": "Chinese",
    "ja": "Japanese",
    "ko": "Korean",
    "ta": "Tamil",
    "th": "Thai",
    "id": "Indonesian",
    "ms": "Malay",
    "vi": "Vietnamese",
}

LOCALIZED_FALLBACK_QUIZZES = {
    "en": {
        "topic_fallback": "this topic",
        "templates": [
            {
                "question": "Which statement is most accurate about {topic}?",
                "options": [
                    "{topic} is mainly used to express a core idea clearly.",
                    "{topic} is only used in mathematics.",
                    "{topic} never appears in real communication.",
                    "{topic} has no rules or patterns.",
                ],
                "correct_index": 0,
                "explanation": "The strongest answer is the one that correctly describes {topic} in real communication.",
            },
            {
                "question": "What is the best first step when learning {topic}?",
                "options": [
                    "Understand the basic rule and review examples.",
                    "Memorize random answers without context.",
                    "Skip practice completely.",
                    "Avoid checking mistakes.",
                ],
                "correct_index": 0,
                "explanation": "A strong first step is to learn the rule and see it used in examples.",
            },
            {
                "question": "Which habit helps improve {topic} the most?",
                "options": [
                    "Regular practice with feedback.",
                    "Practicing once a year.",
                    "Ignoring corrections.",
                    "Using only one-word answers.",
                ],
                "correct_index": 0,
                "explanation": "Consistent practice plus feedback is the most useful improvement habit.",
            },
            {
                "question": "When using {topic}, what should you focus on?",
                "options": [
                    "Meaning, accuracy, and context.",
                    "Only speed, never accuracy.",
                    "Using the longest sentence possible.",
                    "Avoiding all examples.",
                ],
                "correct_index": 0,
                "explanation": "Good performance comes from balancing meaning, accuracy, and context.",
            },
            {
                "question": "Which activity is most useful for mastering {topic}?",
                "options": [
                    "Trying examples and checking why answers are right or wrong.",
                    "Guessing every answer.",
                    "Skipping explanations.",
                    "Studying without a clear topic focus.",
                ],
                "correct_index": 0,
                "explanation": "Worked examples plus explanation review builds durable understanding.",
            },
        ],
    },
    "bn": {
        "topic_fallback": "এই বিষয়টি",
        "templates": [
            {
                "question": "{topic} সম্পর্কে কোন বক্তব্যটি সবচেয়ে সঠিক?",
                "options": [
                    "{topic} মূল ধারণা পরিষ্কারভাবে প্রকাশ করতে বেশি ব্যবহৃত হয়।",
                    "{topic} শুধু গণিতে ব্যবহার হয়।",
                    "{topic} বাস্তব যোগাযোগে কখনও আসে না।",
                    "{topic} এর কোনো নিয়ম বা ধারা নেই।",
                ],
                "correct_index": 0,
                "explanation": "সবচেয়ে ভালো উত্তরটি হলো যেটি বাস্তব যোগাযোগে {topic} কে সঠিকভাবে ব্যাখ্যা করে।",
            },
            {
                "question": "{topic} শিখতে প্রথমে সবচেয়ে ভালো কী করা উচিত?",
                "options": [
                    "মূল নিয়ম বুঝে উদাহরণগুলো দেখা।",
                    "প্রসঙ্গ ছাড়া এলোমেলো উত্তর মুখস্থ করা।",
                    "পুরোপুরি অনুশীলন বাদ দেওয়া।",
                    "ভুলগুলো না দেখা।",
                ],
                "correct_index": 0,
                "explanation": "শুরুতে নিয়ম বোঝা এবং উদাহরণে তা দেখা সবচেয়ে শক্ত ভিত্তি তৈরি করে।",
            },
            {
                "question": "কোন অভ্যাসটি {topic} সবচেয়ে বেশি উন্নত করতে সাহায্য করে?",
                "options": [
                    "নিয়মিত অনুশীলন ও ফিডব্যাক নেওয়া।",
                    "বছরে একবার অনুশীলন করা।",
                    "সংশোধন উপেক্ষা করা।",
                    "শুধু এক শব্দের উত্তর ব্যবহার করা।",
                ],
                "correct_index": 0,
                "explanation": "নিয়মিত অনুশীলন আর ফিডব্যাক উন্নতির সবচেয়ে কার্যকর উপায়।",
            },
            {
                "question": "{topic} ব্যবহার করার সময় কোন বিষয়ে বেশি মনোযোগ দেওয়া উচিত?",
                "options": [
                    "অর্থ, শুদ্ধতা এবং প্রসঙ্গ।",
                    "শুধু গতি, শুদ্ধতা নয়।",
                    "সবচেয়ে বড় বাক্য বানানো।",
                    "সব উদাহরণ এড়িয়ে যাওয়া।",
                ],
                "correct_index": 0,
                "explanation": "ভালো পারফরম্যান্সের জন্য অর্থ, শুদ্ধতা আর প্রসঙ্গের ভারসাম্য দরকার।",
            },
            {
                "question": "{topic} ভালোভাবে আয়ত্ত করতে কোন কাজটি সবচেয়ে উপকারী?",
                "options": [
                    "উদাহরণ অনুশীলন করা এবং কেন উত্তর সঠিক বা ভুল তা দেখা।",
                    "প্রতিটি উত্তর আন্দাজ করা।",
                    "ব্যাখ্যা বাদ দেওয়া।",
                    "স্পষ্ট বিষয় ছাড়া পড়াশোনা করা।",
                ],
                "correct_index": 0,
                "explanation": "উদাহরণ নিয়ে কাজ করা এবং ব্যাখ্যা দেখা শেখাকে দীর্ঘস্থায়ী করে।",
            },
        ],
    },
    "hi": {
        "topic_fallback": "यह विषय",
        "templates": [
            {
                "question": "{topic} के बारे में कौन-सा कथन सबसे सही है?",
                "options": [
                    "{topic} का उपयोग मुख्य विचार को साफ़ तरीके से व्यक्त करने के लिए होता है।",
                    "{topic} केवल गणित में उपयोग होता है।",
                    "{topic} वास्तविक संचार में कभी नहीं आता।",
                    "{topic} का कोई नियम या पैटर्न नहीं है।",
                ],
                "correct_index": 0,
                "explanation": "सबसे अच्छा उत्तर वही है जो वास्तविक संचार में {topic} को सही तरह समझाता है।",
            },
            {
                "question": "{topic} सीखने की सबसे अच्छी पहली शुरुआत क्या है?",
                "options": [
                    "मूल नियम समझना और उदाहरण देखना।",
                    "बिना संदर्भ के यादृच्छिक उत्तर रटना।",
                    "अभ्यास को पूरी तरह छोड़ देना।",
                    "गलतियों की जाँच न करना।",
                ],
                "correct_index": 0,
                "explanation": "शुरुआत में नियम समझना और उसे उदाहरणों में देखना सबसे मजबूत कदम है।",
            },
            {
                "question": "कौन-सी आदत {topic} को सबसे अधिक बेहतर बनाती है?",
                "options": [
                    "नियमित अभ्यास और प्रतिक्रिया लेना।",
                    "साल में एक बार अभ्यास करना।",
                    "सुधारों को नज़रअंदाज़ करना।",
                    "केवल एक-शब्द वाले उत्तर देना।",
                ],
                "correct_index": 0,
                "explanation": "नियमित अभ्यास और प्रतिक्रिया सबसे उपयोगी सुधार की आदत है।",
            },
            {
                "question": "{topic} का उपयोग करते समय किस पर ध्यान देना चाहिए?",
                "options": [
                    "अर्थ, शुद्धता और संदर्भ पर।",
                    "केवल गति पर, शुद्धता पर नहीं।",
                    "सबसे लंबा वाक्य बनाने पर।",
                    "सभी उदाहरणों से बचने पर।",
                ],
                "correct_index": 0,
                "explanation": "अच्छा प्रदर्शन अर्थ, शुद्धता और संदर्भ के संतुलन से आता है।",
            },
            {
                "question": "{topic} में महारत पाने के लिए कौन-सी गतिविधि सबसे उपयोगी है?",
                "options": [
                    "उदाहरणों को आज़माना और समझना कि उत्तर सही या गलत क्यों है।",
                    "हर उत्तर का अनुमान लगाना।",
                    "व्याख्या छोड़ देना।",
                    "बिना स्पष्ट विषय के पढ़ना।",
                ],
                "correct_index": 0,
                "explanation": "उदाहरणों के साथ अभ्यास और व्याख्या की समीक्षा समझ को मजबूत बनाती है।",
            },
        ],
    },
    "ur": {
        "topic_fallback": "یہ موضوع",
        "templates": [
            {
                "question": "{topic} کے بارے میں سب سے درست بیان کون سا ہے؟",
                "options": [
                    "{topic} زیادہ تر ایک بنیادی خیال کو واضح طور پر بیان کرنے کے لیے استعمال ہوتا ہے۔",
                    "{topic} صرف ریاضی میں استعمال ہوتا ہے۔",
                    "{topic} حقیقی گفتگو میں کبھی نہیں آتا۔",
                    "{topic} کا کوئی اصول یا انداز نہیں ہے۔",
                ],
                "correct_index": 0,
                "explanation": "بہترین جواب وہ ہے جو حقیقی گفتگو میں {topic} کی درست وضاحت کرے۔",
            },
            {
                "question": "{topic} سیکھنے کا بہترین پہلا قدم کیا ہے؟",
                "options": [
                    "بنیادی اصول سمجھنا اور مثالیں دیکھنا۔",
                    "بغیر سیاق کے بے ترتیب جواب رٹ لینا۔",
                    "مشق کو مکمل طور پر چھوڑ دینا۔",
                    "غلطیوں کو چیک نہ کرنا۔",
                ],
                "correct_index": 0,
                "explanation": "ابتدا میں اصول سمجھنا اور اسے مثالوں میں دیکھنا سب سے مضبوط قدم ہے۔",
            },
            {
                "question": "کون سی عادت {topic} کو سب سے زیادہ بہتر بناتی ہے؟",
                "options": [
                    "باقاعدہ مشق اور فیڈبیک لینا۔",
                    "سال میں ایک بار مشق کرنا۔",
                    "درستگی کو نظر انداز کرنا۔",
                    "صرف ایک لفظی جواب استعمال کرنا۔",
                ],
                "correct_index": 0,
                "explanation": "باقاعدہ مشق اور فیڈبیک بہتری کی سب سے مؤثر عادت ہے۔",
            },
            {
                "question": "{topic} استعمال کرتے وقت کس چیز پر توجہ دینی چاہیے؟",
                "options": [
                    "مطلب، درستگی اور سیاق پر۔",
                    "صرف رفتار پر، درستگی پر نہیں۔",
                    "سب سے لمبا جملہ بنانے پر۔",
                    "تمام مثالوں سے بچنے پر۔",
                ],
                "correct_index": 0,
                "explanation": "اچھی کارکردگی مطلب، درستگی اور سیاق کے توازن سے آتی ہے۔",
            },
            {
                "question": "{topic} میں مہارت حاصل کرنے کے لیے کون سی سرگرمی سب سے مفید ہے؟",
                "options": [
                    "مثالیں حل کرنا اور دیکھنا کہ جواب درست یا غلط کیوں ہے۔",
                    "ہر جواب کا اندازہ لگانا۔",
                    "وضاحت کو چھوڑ دینا۔",
                    "واضح موضوع کے بغیر پڑھنا۔",
                ],
                "correct_index": 0,
                "explanation": "مثالوں کے ساتھ مشق اور وضاحت کا جائزہ سمجھ کو مضبوط بناتا ہے۔",
            },
        ],
    },
    "ar": {
        "topic_fallback": "هذا الموضوع",
        "templates": [
            {
                "question": "ما العبارة الأكثر دقة حول {topic}؟",
                "options": [
                    "يُستخدم {topic} غالبًا للتعبير عن فكرة أساسية بوضوح.",
                    "يُستخدم {topic} في الرياضيات فقط.",
                    "لا يظهر {topic} أبدًا في التواصل الحقيقي.",
                    "ليس لدى {topic} أي قواعد أو أنماط.",
                ],
                "correct_index": 0,
                "explanation": "أفضل إجابة هي التي تصف {topic} بشكل صحيح في التواصل الحقيقي.",
            },
            {
                "question": "ما أفضل خطوة أولى عند تعلم {topic}؟",
                "options": [
                    "فهم القاعدة الأساسية ومراجعة الأمثلة.",
                    "حفظ إجابات عشوائية بلا سياق.",
                    "تجاهل التدريب تمامًا.",
                    "عدم مراجعة الأخطاء.",
                ],
                "correct_index": 0,
                "explanation": "البداية القوية تكون بفهم القاعدة ورؤيتها في أمثلة واضحة.",
            },
            {
                "question": "أي عادة تساعد أكثر على تحسين {topic}؟",
                "options": [
                    "التدرب بانتظام مع الحصول على تغذية راجعة.",
                    "التدرب مرة واحدة في السنة.",
                    "تجاهل التصحيحات.",
                    "استخدام إجابات من كلمة واحدة فقط.",
                ],
                "correct_index": 0,
                "explanation": "الاستمرار في التدريب مع التغذية الراجعة هو أكثر العادات فائدة للتحسن.",
            },
            {
                "question": "عند استخدام {topic}، على ماذا يجب التركيز؟",
                "options": [
                    "المعنى والدقة والسياق.",
                    "السرعة فقط دون الدقة.",
                    "استخدام أطول جملة ممكنة.",
                    "تجنب جميع الأمثلة.",
                ],
                "correct_index": 0,
                "explanation": "الأداء الجيد يأتي من موازنة المعنى والدقة والسياق.",
            },
            {
                "question": "أي نشاط هو الأكثر فائدة لإتقان {topic}؟",
                "options": [
                    "تجربة الأمثلة ومعرفة سبب صحة الإجابات أو خطئها.",
                    "تخمين كل الإجابات.",
                    "تجاوز الشروحات.",
                    "الدراسة دون تركيز واضح على الموضوع.",
                ],
                "correct_index": 0,
                "explanation": "العمل على أمثلة مع مراجعة التفسير يبني فهمًا أقوى وأكثر ثباتًا.",
            },
        ],
    },
    "zh": {
        "topic_fallback": "这个主题",
        "templates": [
            {
                "question": "关于{topic}，哪一种说法最准确？",
                "options": [
                    "{topic}主要用于清晰表达一个核心意思。",
                    "{topic}只用于数学。",
                    "{topic}在真实交流中从不出现。",
                    "{topic}没有任何规则或模式。",
                ],
                "correct_index": 0,
                "explanation": "最好的答案是能够正确说明{topic}在真实交流中的作用。",
            },
            {
                "question": "学习{topic}时，最好的第一步是什么？",
                "options": [
                    "先理解基本规则，再看例子。",
                    "不看语境就死记随机答案。",
                    "完全跳过练习。",
                    "不检查错误。",
                ],
                "correct_index": 0,
                "explanation": "先理解规则并在例子中看到它，是最稳妥的开始方式。",
            },
            {
                "question": "哪一种习惯最能帮助提升{topic}？",
                "options": [
                    "定期练习并获得反馈。",
                    "一年练习一次。",
                    "忽略纠正意见。",
                    "只用一个词作答。",
                ],
                "correct_index": 0,
                "explanation": "持续练习加上反馈，是最有效的提升习惯。",
            },
            {
                "question": "使用{topic}时，最应该关注什么？",
                "options": [
                    "意思、准确性和语境。",
                    "只要速度，不管准确性。",
                    "尽量用最长的句子。",
                    "避免所有例子。",
                ],
                "correct_index": 0,
                "explanation": "好的表现来自意思、准确性和语境之间的平衡。",
            },
            {
                "question": "要真正掌握{topic}，哪种活动最有帮助？",
                "options": [
                    "练习例子并检查答案为什么对或错。",
                    "每道题都靠猜。",
                    "跳过解释。",
                    "没有明确主题地学习。",
                ],
                "correct_index": 0,
                "explanation": "通过例子练习并复习解释，可以建立更稳固的理解。",
            },
        ],
    },
    "ja": {
        "topic_fallback": "このトピック",
        "templates": [
            {
                "question": "{topic}について最も正しい説明はどれですか。",
                "options": [
                    "{topic}は主な考えを分かりやすく伝えるためによく使われます。",
                    "{topic}は数学でしか使われません。",
                    "{topic}は実際の会話ではまったく出てきません。",
                    "{topic}には規則や型がありません。",
                ],
                "correct_index": 0,
                "explanation": "最もよい答えは、実際のコミュニケーションでの{topic}を正しく説明しているものです。",
            },
            {
                "question": "{topic}を学ぶとき、最初にするべきことは何ですか。",
                "options": [
                    "基本ルールを理解し、例を確認すること。",
                    "文脈なしで答えを丸暗記すること。",
                    "練習を完全に飛ばすこと。",
                    "間違いを確認しないこと。",
                ],
                "correct_index": 0,
                "explanation": "最初はルールを理解し、それが例でどう使われるかを見るのが大切です。",
            },
            {
                "question": "{topic}を最も伸ばす習慣はどれですか。",
                "options": [
                    "定期的に練習し、フィードバックを受けること。",
                    "年に一度だけ練習すること。",
                    "訂正を無視すること。",
                    "一語だけで答えること。",
                ],
                "correct_index": 0,
                "explanation": "継続的な練習とフィードバックが、最も効果的な改善方法です。",
            },
            {
                "question": "{topic}を使うとき、何に注意すべきですか。",
                "options": [
                    "意味、正確さ、文脈。",
                    "速さだけで、正確さは気にしないこと。",
                    "できるだけ長い文を使うこと。",
                    "すべての例を避けること。",
                ],
                "correct_index": 0,
                "explanation": "よいパフォーマンスは、意味と正確さと文脈のバランスから生まれます。",
            },
            {
                "question": "{topic}をしっかり身につけるために最も役立つ活動はどれですか。",
                "options": [
                    "例を試し、なぜ正解か不正解かを確認すること。",
                    "すべての答えを勘で選ぶこと。",
                    "解説を読まないこと。",
                    "はっきりしたテーマなしで勉強すること。",
                ],
                "correct_index": 0,
                "explanation": "例に取り組み、解説を見直すことで理解がより定着します。",
            },
        ],
    },
    "ko": {
        "topic_fallback": "이 주제",
        "templates": [
            {
                "question": "{topic}에 대한 설명으로 가장 정확한 것은 무엇인가요?",
                "options": [
                    "{topic}은 핵심 생각을 분명하게 표현할 때 주로 사용됩니다.",
                    "{topic}은 수학에서만 사용됩니다.",
                    "{topic}은 실제 의사소통에 전혀 나타나지 않습니다.",
                    "{topic}에는 규칙이나 패턴이 없습니다.",
                ],
                "correct_index": 0,
                "explanation": "가장 좋은 답은 실제 의사소통에서 {topic}을 올바르게 설명하는 답입니다.",
            },
            {
                "question": "{topic}을 배울 때 가장 좋은 첫 단계는 무엇인가요?",
                "options": [
                    "기본 규칙을 이해하고 예문을 살펴보는 것.",
                    "문맥 없이 무작위 답을 외우는 것.",
                    "연습을 완전히 건너뛰는 것.",
                    "실수를 확인하지 않는 것.",
                ],
                "correct_index": 0,
                "explanation": "처음에는 규칙을 이해하고 예문 속에서 확인하는 것이 가장 좋습니다.",
            },
            {
                "question": "{topic} 실력을 가장 잘 높여 주는 습관은 무엇인가요?",
                "options": [
                    "규칙적으로 연습하고 피드백을 받는 것.",
                    "일 년에 한 번 연습하는 것.",
                    "수정을 무시하는 것.",
                    "한 단어로만 답하는 것.",
                ],
                "correct_index": 0,
                "explanation": "꾸준한 연습과 피드백이 가장 효과적인 향상 방법입니다.",
            },
            {
                "question": "{topic}을 사용할 때 무엇에 집중해야 하나요?",
                "options": [
                    "의미, 정확성, 그리고 맥락.",
                    "정확성보다 속도만.",
                    "가장 긴 문장 만들기.",
                    "모든 예시 피하기.",
                ],
                "correct_index": 0,
                "explanation": "좋은 수행은 의미와 정확성, 맥락의 균형에서 나옵니다.",
            },
            {
                "question": "{topic}을 제대로 익히는 데 가장 도움이 되는 활동은 무엇인가요?",
                "options": [
                    "예문을 풀어 보고 왜 맞고 틀린지 확인하는 것.",
                    "모든 답을 추측하는 것.",
                    "설명을 건너뛰는 것.",
                    "분명한 주제 없이 공부하는 것.",
                ],
                "correct_index": 0,
                "explanation": "예문 연습과 해설 검토는 이해를 더 오래 남게 합니다.",
            },
        ],
    },
    "ta": {
        "topic_fallback": "இந்த தலைப்பு",
        "templates": [
            {
                "question": "{topic} பற்றி மிகவும் சரியான கூற்று எது?",
                "options": [
                    "{topic} ஒரு முக்கிய கருத்தை தெளிவாக சொல்லப் பயன்படுகிறது.",
                    "{topic} கணிதத்தில் மட்டுமே பயன்படுத்தப்படுகிறது.",
                    "{topic} உண்மையான தொடர்பில் ஒருபோதும் வராது.",
                    "{topic} க்கு எந்த விதியும் அல்லது வடிவமும் இல்லை.",
                ],
                "correct_index": 0,
                "explanation": "உண்மையான தொடர்பில் {topic} எப்படி பயன்படுகிறது என்பதை சரியாக சொல்வதே சிறந்த பதில்.",
            },
            {
                "question": "{topic} கற்றுக்கொள்ள சிறந்த முதல் படி எது?",
                "options": [
                    "அடிப்படை விதியை புரிந்து கொண்டு எடுத்துக்காட்டுகளை பார்க்க வேண்டும்.",
                    "சூழல் இல்லாமல் சீரற்ற பதில்களை மனப்பாடம் செய்ய வேண்டும்.",
                    "பயிற்சியை முழுவதும் தவிர்க்க வேண்டும்.",
                    "தவறுகளைச் சரிபார்க்க வேண்டாம்.",
                ],
                "correct_index": 0,
                "explanation": "முதலில் விதியை புரிந்து கொண்டு அதை எடுத்துக்காட்டுகளில் பார்ப்பது நல்ல தொடக்கம்.",
            },
            {
                "question": "{topic} மேம்பட எந்த பழக்கம் அதிகம் உதவுகிறது?",
                "options": [
                    "தொடர்ச்சியான பயிற்சி மற்றும் பின்னூட்டம் பெறுதல்.",
                    "வருடத்திற்கு ஒருமுறை மட்டும் பயிற்சி செய்தல்.",
                    "திருத்தங்களை புறக்கணித்தல்.",
                    "ஒரே ஒரு சொல் கொண்ட பதில்கள் மட்டும் பயன்படுத்துதல்.",
                ],
                "correct_index": 0,
                "explanation": "தொடர்ச்சியான பயிற்சியும் பின்னூட்டமும் மேம்பாட்டிற்கு மிகவும் பயனுள்ளவை.",
            },
            {
                "question": "{topic} பயன்படுத்தும்போது எந்த விஷயத்தில் கவனம் செலுத்த வேண்டும்?",
                "options": [
                    "பொருள், துல்லியம், மற்றும் சூழல்.",
                    "துல்லியத்தை விட வேகத்தில் மட்டும்.",
                    "மிக நீளமான வாக்கியம் உருவாக்குதல்.",
                    "எல்லா எடுத்துக்காட்டுகளையும் தவிர்த்தல்.",
                ],
                "correct_index": 0,
                "explanation": "நல்ல செயல்திறன் பொருள், துல்லியம், சூழல் ஆகியவற்றின் சமநிலையிலிருந்து வருகிறது.",
            },
            {
                "question": "{topic} நன்றாக கற்றுக்கொள்ள எந்த செயல் மிகவும் உதவுகிறது?",
                "options": [
                    "எடுத்துக்காட்டுகளை செய்து, ஏன் பதில் சரி அல்லது தவறு என்று பார்ப்பது.",
                    "ஒவ்வொரு பதிலும் ஊகித்தல்.",
                    "விளக்கத்தைத் தவிர்த்தல்.",
                    "தெளிவான தலைப்பு இல்லாமல் படித்தல்.",
                ],
                "correct_index": 0,
                "explanation": "எடுத்துக்காட்டுகளுடன் பயிற்சி செய்து விளக்கத்தைப் பார்ப்பது புரிதலை உறுதிசெய்கிறது.",
            },
        ],
    },
    "th": {
        "topic_fallback": "หัวข้อนี้",
        "templates": [
            {
                "question": "ข้อใดอธิบายเกี่ยวกับ {topic} ได้ถูกต้องที่สุด",
                "options": [
                    "{topic} ใช้เพื่อสื่อความหมายหลักให้ชัดเจนเป็นส่วนใหญ่",
                    "{topic} ใช้เฉพาะในคณิตศาสตร์เท่านั้น",
                    "{topic} ไม่เคยพบในสถานการณ์สื่อสารจริง",
                    "{topic} ไม่มีหลักหรือรูปแบบใดเลย",
                ],
                "correct_index": 0,
                "explanation": "คำตอบที่ดีที่สุดคือคำตอบที่อธิบาย {topic} ได้ถูกต้องในบริบทการสื่อสารจริง",
            },
            {
                "question": "ขั้นตอนแรกที่ดีที่สุดในการเรียน {topic} คืออะไร",
                "options": [
                    "เข้าใจกฎพื้นฐานและดูตัวอย่างประกอบ",
                    "ท่องจำคำตอบแบบสุ่มโดยไม่มีบริบท",
                    "ข้ามการฝึกทั้งหมด",
                    "ไม่ตรวจสอบข้อผิดพลาด",
                ],
                "correct_index": 0,
                "explanation": "การเริ่มจากเข้าใจกฎและเห็นการใช้ในตัวอย่างเป็นพื้นฐานที่ดีมาก",
            },
            {
                "question": "นิสัยใดช่วยพัฒนา {topic} ได้มากที่สุด",
                "options": [
                    "ฝึกอย่างสม่ำเสมอและรับคำแนะนำกลับ",
                    "ฝึกปีละครั้ง",
                    "ไม่สนใจการแก้ไข",
                    "ตอบเพียงคำเดียวเท่านั้น",
                ],
                "correct_index": 0,
                "explanation": "การฝึกอย่างต่อเนื่องพร้อมคำแนะนำกลับเป็นวิธีพัฒนาที่มีประโยชน์ที่สุด",
            },
            {
                "question": "เมื่อใช้ {topic} ควรให้ความสำคัญกับอะไร",
                "options": [
                    "ความหมาย ความถูกต้อง และบริบท",
                    "เน้นความเร็วอย่างเดียวไม่ต้องถูกต้อง",
                    "ใช้ประโยคให้ยาวที่สุด",
                    "หลีกเลี่ยงตัวอย่างทั้งหมด",
                ],
                "correct_index": 0,
                "explanation": "ผลลัพธ์ที่ดีมาจากความสมดุลของความหมาย ความถูกต้อง และบริบท",
            },
            {
                "question": "กิจกรรมใดมีประโยชน์ที่สุดต่อการเชี่ยวชาญ {topic}",
                "options": [
                    "ลองทำตัวอย่างและตรวจว่าทำไมคำตอบจึงถูกหรือผิด",
                    "เดาคำตอบทุกข้อ",
                    "ข้ามคำอธิบาย",
                    "เรียนโดยไม่มีหัวข้อชัดเจน",
                ],
                "correct_index": 0,
                "explanation": "การฝึกกับตัวอย่างและทบทวนคำอธิบายช่วยให้เข้าใจได้มั่นคงขึ้น",
            },
        ],
    },
    "id": {
        "topic_fallback": "topik ini",
        "templates": [
            {
                "question": "Pernyataan mana yang paling tepat tentang {topic}?",
                "options": [
                    "{topic} terutama digunakan untuk menyampaikan gagasan inti dengan jelas.",
                    "{topic} hanya digunakan dalam matematika.",
                    "{topic} tidak pernah muncul dalam komunikasi nyata.",
                    "{topic} tidak memiliki aturan atau pola.",
                ],
                "correct_index": 0,
                "explanation": "Jawaban terbaik adalah yang menjelaskan {topic} dengan benar dalam komunikasi nyata.",
            },
            {
                "question": "Langkah pertama terbaik saat mempelajari {topic} adalah apa?",
                "options": [
                    "Memahami aturan dasar dan meninjau contoh.",
                    "Menghafal jawaban acak tanpa konteks.",
                    "Melewatkan latihan sepenuhnya.",
                    "Tidak memeriksa kesalahan.",
                ],
                "correct_index": 0,
                "explanation": "Awal yang kuat adalah memahami aturan dan melihatnya dalam contoh.",
            },
            {
                "question": "Kebiasaan mana yang paling membantu meningkatkan {topic}?",
                "options": [
                    "Berlatih secara teratur dengan umpan balik.",
                    "Berlatih sekali setahun.",
                    "Mengabaikan koreksi.",
                    "Hanya menggunakan jawaban satu kata.",
                ],
                "correct_index": 0,
                "explanation": "Latihan yang konsisten ditambah umpan balik adalah kebiasaan perbaikan yang paling berguna.",
            },
            {
                "question": "Saat menggunakan {topic}, apa yang harus menjadi fokus?",
                "options": [
                    "Makna, ketepatan, dan konteks.",
                    "Hanya kecepatan, bukan ketepatan.",
                    "Menggunakan kalimat paling panjang.",
                    "Menghindari semua contoh.",
                ],
                "correct_index": 0,
                "explanation": "Performa yang baik datang dari keseimbangan antara makna, ketepatan, dan konteks.",
            },
            {
                "question": "Kegiatan mana yang paling berguna untuk menguasai {topic}?",
                "options": [
                    "Mencoba contoh dan memeriksa mengapa jawaban benar atau salah.",
                    "Menebak semua jawaban.",
                    "Melewati penjelasan.",
                    "Belajar tanpa fokus topik yang jelas.",
                ],
                "correct_index": 0,
                "explanation": "Latihan melalui contoh dan meninjau penjelasan membangun pemahaman yang lebih kuat.",
            },
        ],
    },
    "ms": {
        "topic_fallback": "topik ini",
        "templates": [
            {
                "question": "Pernyataan manakah yang paling tepat tentang {topic}?",
                "options": [
                    "{topic} biasanya digunakan untuk menyampaikan idea utama dengan jelas.",
                    "{topic} hanya digunakan dalam matematik.",
                    "{topic} tidak pernah muncul dalam komunikasi sebenar.",
                    "{topic} tidak mempunyai peraturan atau pola.",
                ],
                "correct_index": 0,
                "explanation": "Jawapan terbaik ialah jawapan yang menerangkan {topic} dengan betul dalam komunikasi sebenar.",
            },
            {
                "question": "Apakah langkah pertama terbaik semasa mempelajari {topic}?",
                "options": [
                    "Memahami peraturan asas dan melihat contoh.",
                    "Menghafal jawapan rawak tanpa konteks.",
                    "Melangkau latihan sepenuhnya.",
                    "Tidak menyemak kesilapan.",
                ],
                "correct_index": 0,
                "explanation": "Permulaan yang kuat ialah memahami peraturan dan melihat penggunaannya dalam contoh.",
            },
            {
                "question": "Tabiat manakah paling membantu meningkatkan {topic}?",
                "options": [
                    "Berlatih secara konsisten dengan maklum balas.",
                    "Berlatih sekali setahun.",
                    "Mengabaikan pembetulan.",
                    "Hanya menggunakan jawapan satu perkataan.",
                ],
                "correct_index": 0,
                "explanation": "Latihan yang konsisten bersama maklum balas ialah tabiat penambahbaikan yang paling berguna.",
            },
            {
                "question": "Apabila menggunakan {topic}, apakah yang perlu diberi tumpuan?",
                "options": [
                    "Makna, ketepatan, dan konteks.",
                    "Kelajuan sahaja tanpa ketepatan.",
                    "Menggunakan ayat yang paling panjang.",
                    "Mengelakkan semua contoh.",
                ],
                "correct_index": 0,
                "explanation": "Prestasi yang baik datang daripada keseimbangan antara makna, ketepatan, dan konteks.",
            },
            {
                "question": "Aktiviti manakah paling berguna untuk menguasai {topic}?",
                "options": [
                    "Mencuba contoh dan menyemak mengapa jawapan betul atau salah.",
                    "Meneka semua jawapan.",
                    "Melangkau penjelasan.",
                    "Belajar tanpa fokus topik yang jelas.",
                ],
                "correct_index": 0,
                "explanation": "Latihan melalui contoh dan semakan penjelasan membina kefahaman yang lebih kukuh.",
            },
        ],
    },
    "vi": {
        "topic_fallback": "chủ đề này",
        "templates": [
            {
                "question": "Phát biểu nào chính xác nhất về {topic}?",
                "options": [
                    "{topic} chủ yếu được dùng để diễn đạt rõ một ý chính.",
                    "{topic} chỉ được dùng trong toán học.",
                    "{topic} không bao giờ xuất hiện trong giao tiếp thực tế.",
                    "{topic} không có quy tắc hay mẫu nào.",
                ],
                "correct_index": 0,
                "explanation": "Câu trả lời tốt nhất là câu mô tả đúng {topic} trong giao tiếp thực tế.",
            },
            {
                "question": "Bước đầu tiên tốt nhất khi học {topic} là gì?",
                "options": [
                    "Hiểu quy tắc cơ bản và xem ví dụ.",
                    "Học thuộc các câu trả lời ngẫu nhiên không có ngữ cảnh.",
                    "Bỏ qua hoàn toàn việc luyện tập.",
                    "Không kiểm tra lỗi.",
                ],
                "correct_index": 0,
                "explanation": "Một khởi đầu tốt là hiểu quy tắc và thấy nó xuất hiện trong ví dụ.",
            },
            {
                "question": "Thói quen nào giúp cải thiện {topic} nhiều nhất?",
                "options": [
                    "Luyện tập đều đặn và nhận phản hồi.",
                    "Luyện tập mỗi năm một lần.",
                    "Bỏ qua các sửa lỗi.",
                    "Chỉ dùng câu trả lời một từ.",
                ],
                "correct_index": 0,
                "explanation": "Luyện tập đều đặn cùng phản hồi là thói quen cải thiện hữu ích nhất.",
            },
            {
                "question": "Khi sử dụng {topic}, bạn nên tập trung vào điều gì?",
                "options": [
                    "Ý nghĩa, độ chính xác và ngữ cảnh.",
                    "Chỉ tốc độ mà không cần chính xác.",
                    "Dùng câu dài nhất có thể.",
                    "Tránh mọi ví dụ.",
                ],
                "correct_index": 0,
                "explanation": "Kết quả tốt đến từ sự cân bằng giữa ý nghĩa, độ chính xác và ngữ cảnh.",
            },
            {
                "question": "Hoạt động nào hữu ích nhất để thành thạo {topic}?",
                "options": [
                    "Làm ví dụ và kiểm tra vì sao đáp án đúng hoặc sai.",
                    "Đoán mọi đáp án.",
                    "Bỏ qua phần giải thích.",
                    "Học mà không có trọng tâm rõ ràng.",
                ],
                "correct_index": 0,
                "explanation": "Luyện qua ví dụ và xem lại phần giải thích giúp tạo ra hiểu biết bền vững hơn.",
            },
        ],
    },
}


class QuizGenerateRequest(BaseModel):
    topic: str
    subject: Optional[str] = None
    difficulty: str = "intermediate"
    num_questions: int = 5
    language: str = "en"


class QuizSubmitRequest(BaseModel):
    result_id: int
    answers: List[int]


def get_time_per_question(difficulty: str) -> int:
    return 30 if difficulty == "advanced" else 50


def check_quiz_limit(user: User, db: Session):
    print(f"[QUIZ] User: {user.email}, Role: {user.role}, Plan: {user.subscription_plan}")

    if user.role in ("admin", "superadmin"):
        print("[QUIZ] Admin detected - no limits applied")
        return

    plan = user.subscription_plan or "free"
    limits = QUIZ_LIMITS.get(plan, QUIZ_LIMITS["free"])

    daily_limit = limits.get("daily")
    weekly_limit = limits.get("weekly")
    monthly_limit = limits.get("monthly")

    if daily_limit is None and weekly_limit is None and monthly_limit is None:
        print("[QUIZ] Premium detected - no limits applied")
        return

    today = date.today()
    last_reset = user.last_usage_reset.date() if user.last_usage_reset else None
    if last_reset != today:
        user.quiz_generated_today = 0
        user.last_usage_reset = datetime.utcnow()
        db.commit()

    if daily_limit is not None and user.quiz_generated_today >= daily_limit:
        raise HTTPException(402, f"Daily quiz limit ({daily_limit}) reached for {plan} plan. Try tomorrow!")

    if weekly_limit is not None:
        week_ago = datetime.utcnow() - timedelta(days=7)
        weekly_count = db.query(QuizResult).filter(
            and_(QuizResult.user_id == user.id, QuizResult.created_at >= week_ago)
        ).count()
        if weekly_count >= weekly_limit:
            raise HTTPException(402, f"Weekly quiz limit ({weekly_limit}) reached. Try next week!")

    if monthly_limit is not None:
        month_ago = datetime.utcnow() - timedelta(days=30)
        monthly_count = db.query(QuizResult).filter(
            and_(QuizResult.user_id == user.id, QuizResult.created_at >= month_ago)
        ).count()
        if monthly_count >= monthly_limit:
            raise HTTPException(402, f"Monthly quiz limit ({monthly_limit}) reached. Try next month!")

    user.quiz_generated_today += 1
    db.commit()


def build_fallback_quiz(topic: str, num_questions: int, language: str = "en"):
    localized_pack = LOCALIZED_FALLBACK_QUIZZES.get(language, LOCALIZED_FALLBACK_QUIZZES["en"])
    normalized_topic = topic.strip() or localized_pack["topic_fallback"]
    templates = localized_pack["templates"]
    questions = []

    for index in range(num_questions):
        template = templates[index % len(templates)]
        questions.append({
            "question": template["question"].format(topic=normalized_topic),
            "options": [option.format(topic=normalized_topic) for option in template["options"]],
            "correct_index": template["correct_index"],
            "explanation": template["explanation"].format(topic=normalized_topic),
        })

    return questions


def serialize_quiz_leader(row, rank: int):
    return {
        "rank": rank,
        "user_id": row.user_id,
        "name": row.name,
        "avatar": row.avatar,
        "attempts": int(row.attempts or 0),
        "avg_score": round(float(row.avg_score or 0), 1),
        "best_score": round(float(row.best_score or 0), 1),
        "quiz_xp": int(row.quiz_xp or 0),
        "total_correct": int(row.total_correct or 0),
    }


@router.post("/generate")
async def generate_quiz(
    req: QuizGenerateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_quiz_limit(user, db)

    num = min(max(req.num_questions, 3), 15)
    language_code = req.language if req.language in LANGUAGE_LABELS else "en"
    language_name = LANGUAGE_LABELS[language_code]
    time_per_question = get_time_per_question(req.difficulty)

    system = (
        f"You are a quiz generator. Generate exactly {num} multiple choice questions in {language_name}.\n"
        f"Topic: {req.topic}"
        + (f", Subject: {req.subject}" if req.subject else "")
        + f"\nDifficulty: {req.difficulty}\n"
        f"All question text, every option, and every explanation must be written fully in {language_name}.\n"
        "Do not mix languages unless the topic itself requires a proper noun or quoted technical term.\n"
        "Keep the language natural and learner-friendly for the selected audience in Asia when relevant.\n"
        "Each question must have exactly 4 answer options.\n\n"
        "Return ONLY a valid JSON array with no markdown, no backticks, and no extra commentary:\n"
        '[\n  {\n    "question": "...",\n    "options": ["...","...","...","..."],\n'
        '    "correct_index": 0,\n    "explanation": "..."\n  }\n]'
    )
    messages = [{
        "role": "user",
        "content": (
            f"Generate {num} quiz questions about {req.topic} in {language_name}. "
            f"Make sure the question, all options, and the explanation are fully in {language_name}."
        ),
    }]

    try:
        raw, provider = await call_ai(system, messages)
        raw = raw.strip()
        json_match = re.search(r"\[.*\]", raw, re.DOTALL)
        if json_match:
            raw = json_match.group()
        questions = json.loads(raw)

        validated = []
        for question in questions:
            options = question.get("options") or []
            correct_index = question.get("correct_index")
            if (
                isinstance(question.get("question"), str)
                and isinstance(options, list)
                and len(options) >= 4
                and isinstance(correct_index, int)
                and 0 <= correct_index < 4
            ):
                validated.append({
                    "question": question["question"],
                    "options": options[:4],
                    "correct_index": correct_index,
                    "explanation": question.get("explanation", ""),
                })

        if not validated:
            raise ValueError("No valid questions generated")

    except json.JSONDecodeError:
        provider = "local-fallback"
        validated = build_fallback_quiz(req.topic, num, language_code)
    except Exception as exc:
        print(f"[QUIZ] Falling back to local quiz generator: {exc}")
        provider = "local-fallback"
        validated = build_fallback_quiz(req.topic, num, language_code)

    result = QuizResult(
        user_id=user.id,
        topic=req.topic,
        subject=req.subject,
        difficulty=req.difficulty,
        language=language_code,
        total_q=len(validated),
        questions=validated,
    )
    db.add(result)
    db.commit()
    db.refresh(result)

    public_questions = [{"question": q["question"], "options": q["options"]} for q in validated]
    return {
        "result_id": result.id,
        "topic": req.topic,
        "difficulty": req.difficulty,
        "language": language_code,
        "total": len(validated),
        "questions": public_questions,
        "time_per_question": time_per_question,
        "provider": provider,
    }


@router.post("/submit")
def submit_quiz(
    req: QuizSubmitRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = db.query(QuizResult).filter(
        QuizResult.id == req.result_id,
        QuizResult.user_id == user.id,
    ).first()
    if not result:
        raise HTTPException(404, "Quiz not found")

    if result.score > 0:
        raise HTTPException(400, "Quiz already submitted")

    questions = result.questions
    if len(req.answers) != len(questions):
        raise HTTPException(400, f"Expected {len(questions)} answers")

    correct = 0
    feedback = []
    for question, answer in zip(questions, req.answers):
        is_correct = answer == question["correct_index"]
        if is_correct:
            correct += 1
        feedback.append({
            "question": question["question"],
            "your_answer": question["options"][answer] if 0 <= answer < len(question["options"]) else "Invalid",
            "correct_answer": question["options"][question["correct_index"]],
            "is_correct": is_correct,
            "explanation": question.get("explanation", ""),
        })

    score = round((correct / len(questions)) * 100, 1)
    xp_earned = int(score / 10) * 2 + correct * 3

    result.correct = correct
    result.score = score
    result.xp_earned = xp_earned
    user.xp_points += xp_earned
    db.commit()

    return {
        "score": score,
        "correct": correct,
        "total": len(questions),
        "xp_earned": xp_earned,
        "feedback": feedback,
        "passed": score >= 60,
    }


@router.get("/history")
def get_quiz_history(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    results = db.query(QuizResult).filter(
        QuizResult.user_id == user.id
    ).order_by(QuizResult.created_at.desc()).limit(20).all()

    return [{
        "id": result.id,
        "topic": result.topic,
        "subject": result.subject,
        "difficulty": result.difficulty,
        "language": result.language,
        "time_per_question": get_time_per_question(result.difficulty),
        "total_q": result.total_q,
        "correct": result.correct,
        "score": result.score,
        "xp_earned": result.xp_earned,
        "created_at": result.created_at.isoformat(),
        "questions": result.questions if result.questions else [],
    } for result in results]


@router.get("/leaderboard")
def get_quiz_leaderboard(
    limit: int = Query(5, ge=1, le=20),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    attempts = func.count(QuizResult.id).label("attempts")
    avg_score = func.avg(QuizResult.score).label("avg_score")
    best_score = func.max(QuizResult.score).label("best_score")
    quiz_xp = func.sum(QuizResult.xp_earned).label("quiz_xp")
    total_correct = func.sum(QuizResult.correct).label("total_correct")

    rows = db.query(
        User.id.label("user_id"),
        User.name.label("name"),
        User.avatar.label("avatar"),
        attempts,
        avg_score,
        best_score,
        quiz_xp,
        total_correct,
    ).join(
        QuizResult, QuizResult.user_id == User.id
    ).filter(
        User.is_active == True,
        QuizResult.score > 0,
    ).group_by(
        User.id, User.name, User.avatar
    ).order_by(
        avg_score.desc(),
        quiz_xp.desc(),
        attempts.desc(),
        best_score.desc(),
        User.name.asc(),
    ).all()

    serialized = [serialize_quiz_leader(row, index + 1) for index, row in enumerate(rows)]
    leaders = serialized[:limit]
    me = next((row for row in serialized if row["user_id"] == user.id), None)

    return {
        "leaders": leaders,
        "me": me,
    }
