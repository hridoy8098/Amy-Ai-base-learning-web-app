# Models Package
from models.models import *
from models.game_models import *

__all__ = [
    # Existing models
    'User', 'Category', 'Course', 'Lesson', 'Enrollment', 'LessonProgress',
    'Payment', 'QuizResult', 'AmySession', 'AmyMessage', 'Note', 'Bookmark',
    'Badge', 'UserBadge', 'Certificate', 'CourseReview', 'Notification',
    'SavedVocab', 'Coupon', 'FluencyRecord', 'UserMemory', 'GrammarMistake',
    'UserGoal', 'SmartReminder', 'MicroCertificate',
    'PlacementSubject', 'PlacementTopic', 'PlacementLevel', 'PlacementQuestion',
    'UserPlacementProgress', 'PlacementAttempt',
    
    # New Game Learning Models
    'DifficultyEnum', 'LevelTypeEnum', 'QuestionTypeEnum', 'UserTierEnum',
    'QuestionSourceEnum', 'ConfidenceLevelEnum', 'ChallengeStatusEnum',
    
    # Curriculum
    'GameSubject', 'GameTopic', 'GameLevel', 'LevelLock',
    
    # Questions
    'GameQuestion', 'FallbackQuestion', 'QuestionCache',
    
    # User Progress
    'GameUserProgress', 'SubjectProgress', 'TopicProgress', 'LevelProgress',
    'LevelAttempt', 'QuestionResponse',
    
    # Weak Areas & Spaced Repetition
    'WeakArea', 'SpacedRepetitionQueue',
    
    # Gamification
    'DailyMission', 'UserDailyMission', 'GameBadge', 'UserGameBadge',
    'RewardChest', 'Leaderboard', 'FriendChallenge',
    
    # Placement Test
    'PlacementTest', 'PlacementTestResult',
]
