#include "accounts.h"
#include "transactions.h"
#include "schedule.h"
#include "document.h"

int
save_native(
    char *filename,
    char *document_id,
    DocumentProperties *properties,
    AccountList *accounts,
    TransactionList *transactions,
    Schedule **schedules);
