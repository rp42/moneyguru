#include "split.h"
#include "util.h"

void
split_init(
    Split *split, Account *account, const Amount *amount, unsigned int index)
{
    split->account = account;
    amount_copy(&split->amount, amount);
    split->reconciliation_date = 0;
    split->memo = "";
    split->reference = NULL;
    split->index = index;
}

void
split_deinit(Split *split)
{
    strfree(&split->memo);
    strfree(&split->reference);
}

void
split_account_set(Split *split, Account *account)
{
    if (account != split->account) {
        split->reconciliation_date = 0;
        split->account = account;
    }
}

void
split_amount_set(Split *split, const Amount *amount)
{
    if (split->amount.currency && amount->currency != split->amount.currency) {
        split->reconciliation_date = 0;
    }
    amount_copy(&split->amount, amount);
}

bool
split_copy(Split *dst, const Split *src)
{
    dst->account = src->account;
    amount_copy(&dst->amount, &src->amount);
    dst->reconciliation_date = src->reconciliation_date;
    if (!strclone(&dst->memo, src->memo)) {
        return false;
    }
    if (!strclone(&dst->reference, src->reference)) {
        return false;
    }
    return true;
}

bool
split_eq(const Split *s1, const Split *s2)
{
    if (s1->account == NULL) {
        if (s2->account != NULL) {
            return false;
        }
    } else {
        if (s2->account == NULL) {
            return false;
        } else if (strcmp(s1->account->name, s2->account->name) != 0) {
            return false;
        }
    }
    return true;
    if (!amount_eq(&s1->amount, &s2->amount)) {
        return false;
    }
    /*if (strcmp(s1->memo, s2->memo) != 0) {*/
    /*    return false;                     */
    /*}                                     */
    /*if (s1->reconciliation_date != s2->reconciliation_date) {*/
    /*    return false;                                        */
    /*}                                                        */
    return true;
}

