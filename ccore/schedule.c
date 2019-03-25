#include "schedule.h"

/* Private */
static void
_txn_free(gpointer data)
{
    Transaction *txn = data;
    transaction_deinit(txn);
    free(txn);
}

/* Public */
bool
schedule_init(
    Schedule *sched,
    const Transaction *ref,
    RepeatType type,
    unsigned int every)
{
    if (!transaction_copy(&sched->ref, ref)) {
        return false;
    }
    transaction_copy(&sched->ref, ref);
    sched->type = type;
    sched->every = every;
    sched->stop = 0;
    // we use direct time_t values as keys, not pointers
    sched->deletions = g_hash_table_new(g_direct_hash, g_direct_equal);
    sched->globalchanges = g_hash_table_new_full(
        g_direct_hash,
        g_direct_equal,
        NULL,
        _txn_free);
    return true;
}

void
schedule_deinit(Schedule *sched)
{
    g_hash_table_destroy(sched->deletions);
    sched->deletions = NULL;
    g_hash_table_destroy(sched->globalchanges);
    sched->globalchanges = NULL;
}

void
schedule_add_global_change(
    Schedule *sched,
    time_t date,
    const Transaction *txn)
{
    Transaction *toadd = calloc(sizeof(Transaction), 1);
    transaction_copy(toadd, txn);
    g_hash_table_insert(sched->globalchanges, (gpointer)date, toadd);
    schedule_update_ref(sched);
}

bool
schedule_copy(Schedule *dst, const Schedule *src)
{
    if (!schedule_init(dst, &src->ref, src->type, src->every)) {
        return false;
    }
    dst->stop = src->stop;

    schedule_reset_exceptions(dst);
    GHashTableIter iter;
    gpointer key, value;
    g_hash_table_iter_init(&iter, src->deletions);
    while (g_hash_table_iter_next(&iter, &key, &value)) {
        g_hash_table_add(dst->deletions, key);
    }
    g_hash_table_iter_init(&iter, src->globalchanges);
    while (g_hash_table_iter_next(&iter, &key, &value)) {
        Transaction *srcref = value;
        Transaction *dstref = calloc(sizeof(Transaction), 1);
        transaction_copy(dstref, srcref);
        g_hash_table_insert(dst->globalchanges, key, dstref);
    }
    return true;
}

void
schedule_delete_at(Schedule *sched, time_t date)
{
    g_hash_table_add(sched->deletions, (gpointer)date);
    schedule_update_ref(sched);
}

bool
schedule_is_deleted_at(const Schedule *sched, time_t date)
{
    return g_hash_table_contains(sched->deletions, (gpointer)date);
}

GSList*
schedule_get_spawns(Schedule *sched, time_t end)
{
    Transaction *current_ref = &sched->ref;
    time_t start = current_ref->date;
    int incsize = 0;
    time_t global_date_delta = 0;

    GHashTableIter iter;
    gpointer key, value;
    g_hash_table_iter_init(&iter, sched->deletions);
    while (g_hash_table_iter_next(&iter, &key, &value)) {
        if ((time_t)key > end) {
            end = (time_t)key;
        }
    }
    g_hash_table_iter_init(&iter, sched->globalchanges);
    while (g_hash_table_iter_next(&iter, &key, &value)) {
        time_t rd = (time_t)key;
        time_t vd = ((Transaction *)value)->date;
        if (vd < rd) {
            end += (rd - vd);
        }
    }
    if ((sched->stop > 0) && (end > sched->stop)) {
        end = sched->stop;
    }

    GSList *res = NULL;
    while (true) {
        time_t date = inc_date(start, sched->type, incsize);
        incsize += sched->every;
        if (date == -1) {
            continue;
        }
        if (date > end) {
            break;
        }
        Transaction *txn = g_hash_table_lookup(
            sched->globalchanges, (gpointer)date);
        if (txn != NULL) {
            current_ref = txn;
            global_date_delta = current_ref->date - date;
        }
        // if txn != NULL, this schedule period is deleted
        if (!schedule_is_deleted_at(sched, date)) {
            Transaction *spawn = calloc(sizeof(Transaction), 1);
            transaction_copy(spawn, current_ref);
            spawn->type = TXN_TYPE_RECURRENCE;
            spawn->date = date + global_date_delta;
            spawn->recurrence_date = date;
            spawn->ref = current_ref;
            res = g_slist_prepend(res, (gpointer)spawn);
        }
    }
    res = g_slist_reverse(res);
    return res;
}

void
schedule_reset_exceptions(Schedule *sched)
{
    g_hash_table_remove_all(sched->deletions);
    g_hash_table_remove_all(sched->globalchanges);
}

void
schedule_update_ref(Schedule *sched)
{
    time_t date = sched->ref.date;
    while (true) {
        if (!schedule_is_deleted_at(sched, date)) {
            // Not a deleted spawn? we're finished with our loop
            break;
        }
        // We have a deleted spawn. We'll advance our start date
        date = inc_date_skip(date, sched->type, sched->every);
    }
    if (g_hash_table_contains(sched->globalchanges, (gpointer)date)) {
        // We have a global change matching. this is our new ref
        Transaction *txn = g_hash_table_lookup(
            sched->globalchanges, (gpointer)date);
        transaction_copy(&sched->ref, txn);
        g_hash_table_remove(sched->globalchanges, (gpointer)date);
    } else {
        // we just need to advance our new date
        sched->ref.date = date;
    }
    GHashTableIter iter;
    gpointer key, value;
    g_hash_table_iter_init(&iter, sched->deletions);
    while (g_hash_table_iter_next(&iter, &key, &value)) {
        if ((time_t)key <= date) {
            g_hash_table_iter_remove(&iter);
        }
    }
    g_hash_table_iter_init(&iter, sched->globalchanges);
    while (g_hash_table_iter_next(&iter, &key, &value)) {
        if ((time_t)key <= date) {
            g_hash_table_iter_remove(&iter);
        }
    }
}
