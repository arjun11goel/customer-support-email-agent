from enum import Enum


class EmailSource(str, Enum):
    MOCK = "mock"
    GMAIL = "gmail"
    OUTLOOK = "outlook"


class EmailStatus(str, Enum):
    NEW = "new"
    PROCESSING = "processing"
    PROCESSED = "processed"
    NEEDS_REVIEW = "needs_review"
    ESCALATED = "escalated"


class IntentCategory(str, Enum):
    PRODUCT_QUESTION = "product_question"
    BUG_REPORT = "bug_report"
    BILLING_ISSUE = "billing_issue"
    FEATURE_REQUEST = "feature_request"
    COMPLEX_ISSUE = "complex_issue"
    OTHER = "other"