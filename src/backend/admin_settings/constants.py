SETTINGS_CONSTANT = [
    {'title': 'Gender', 'can_disabled': False, 'children': []},
    {'title': 'Category', 'can_disabled': False, 'children': []},
]

ACTION_TYPE_CREATE = "created"
ACTION_TYPE_ADDED = "added"
ACTION_TYPE_BULK_ADDED = "added (in bulk)"
ACTION_TYPE_BULK_DELETED = "deleted (in bulk)"
ACTION_TYPE_REMOVED = "removed"
ACTION_TYPE_UPDATE = "updated"
ACTION_TYPE_APPROVED = "approved"
ACTION_TYPE_DELETE = "deleted"
ACTION_TYPE_REJECTED = "rejected"
ACTION_TYPE_CANCELLED = "cancelled"
ACTION_TYPE_CREDIT = "credited"
ACTION_TYPE_DEBIT = "debited"
ACTION_TYPE_ASSIGN = "assigned"
ACTION_TYPE_RESET_PASSWORD = "reset"
ACTION_TYPE_LOCK = "locked"
ACTION_TYPE_APPLY = "applied"
ACTION_TYPE_SEPARATE = "separated"
ACTION_TYPE_RETRIEVE = "retrieved"
ACTION_TYPE_CLEARED = "cleared"

# Log Actions

ACTION_OBJECT = {
    'Location': 'location',
    'DynamicSettings': 'dynamic setting'
}

# Log Category and sub category
# Categories
SETTINGS = "settings"
PASSWORD = "password"

LOG_STRATA = {}
CREDIT = 'credit'
DEBIT = 'debit'

TRANSACTION_TYPES = (
    (CREDIT, CREDIT),
    (DEBIT, DEBIT),
)

ACTION_CREATE = "credit"
ACTION_UPDATE = "update"
ACTION_DELETE = "delete"
