#pragma once
#include "accounts.h"

typedef struct {
    Account *account;
    Account copy;
} ChangedAccount;

/* References to added and deleted entities are direct references. The
 * AccountList and TransactionList manage a "trash can" and always own those
 * references, which aren't freed until deinit() or clear(). They can thus be
 * undeleted if needed.
 *
 * References to changed entities, however, are copies. To be able to remember
 * changed values, we need to copy those entities. Those copies are owned by
 * the UndoStep.
 * 
 * MEMORY MANAGEMENT: memory model of the UndoStep is sound as long as it is
 * used sanely, that is, in the proper order. Don't undo or redo twice in a
 * row, redo only after an undo, etc. The undo history is linear and that line
 * has to be respected for memory management to stay sound.
 */
typedef struct {
    Account **added_accounts;
    Account **deleted_accounts;
    ChangedAccount *changed_accounts;
    int changed_count;
} UndoStep;

/* This function takes care of make appropriate copies. You should send it
 * straight, uncopied entities.
 */
void
undostep_init(
    UndoStep *step,
    Account **added_accounts,
    Account **deleted_accounts,
    Account **changed_accounts);

void
undostep_deinit(UndoStep *step);

/* Returns whether undo could be completed successfully.
 */
bool
undostep_undo(UndoStep *step, AccountList *alist);

bool
undostep_redo(UndoStep *step, AccountList *alist);
