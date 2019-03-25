#pragma once

#include <glib.h>
#include "transaction.h"
#include "recurrence.h"

/* A recurring transaction
 *
 * One of the great features of moneyGuru is its ability to easy allow
 * exceptions in its schedule.  The amount changes one month? No problem, just
 * change it. The transaction happens a day later?  No problem, change it. From
 * now on, every following transaction is going to happen a day later?  No
 * problem, hold shift when you commit the change to make it "global".
 *
 * All these exceptions, they have to be recorded somewhere. The "one-time"
 * exceptions are kept in :attr:`date2exception`. The date used in the mapping
 * is :attr:`Spawn.recurrent_date` because when we change the date of an
 * exception, we still want to remember which recurrent date it replaces, so we
 * used the date at which the *regular* transaction was supposed to happen.
 *
 * There are also the "global" exceptions, which are stored in
 * :attr:`date2globalchange` and work kinda like normal exception, except that
 * from the date they first happen, all following spawns are going to use this
 * exception as a transaction model. This includes date. That is, if a global
 * exception is 3 days later than its :attr:`Spawn.recurrent_date`, then all
 * following spawns are going to to be 3 days later.
 *
 * Exceptions can override each other. We can be riding on a global exception
 * and, suddenly, a newer global or local exception is there! Well, we apply
 * that exception.
 *
 * An exception can also be a deletion, that is "oh, this week that transaction
 * didn't happen".  This is recorded by putting ``None`` in
 * :attr:`date2exception`. When this deletion is done as a global change (from
 * this date, this schedule doesn't happen anymore), we simply set
 * :attr:`stop_date`.
 */
typedef struct {
    Transaction ref;
    // date at which the schedule stops. 0 if never.
    time_t stop;
    RepeatType type;
    // Repeats every X units of `type`.
    unsigned int every;
    // key-only hash. Contains the recurrence date of deleted occurrences.
    GHashTable *deletions;
    GHashTable *globalchanges;
} Schedule;

// ref is copied, not kept as a pointer.
bool
schedule_init(
    Schedule *sched,
    const Transaction *ref,
    RepeatType type,
    unsigned int every);

void
schedule_deinit(Schedule *sched);

// txn is copied in, not kept as a pointer.
void
schedule_add_global_change(
    Schedule *sched,
    time_t date,
    const Transaction *txn);

// dst has to be deinited
bool
schedule_copy(Schedule *dst, const Schedule *src);

void
schedule_delete_at(Schedule *sched, time_t date);

bool
schedule_is_deleted_at(const Schedule *sched, time_t date);

void
schedule_reset_exceptions(Schedule *sched);

/* Go through our schedule dates and see if we should either move our
 * start date due to deleted spawns or to update or ref transaction due to
 * a global change that end up being on our first schedule date.
 */
void
schedule_update_ref(Schedule *sched);
