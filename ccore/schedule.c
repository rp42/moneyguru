#include "schedule.h"

void
schedule_init(
    Schedule *sched,
    const Transaction *ref,
    RepeatType type,
    unsigned int every)
{
    transaction_copy(&sched->ref, ref);
    sched->type = type;
    sched->every = every;
    sched->stop = 0;
}

bool
schedule_copy(Schedule *dst, const Schedule *src)
{
    if (!transaction_copy(&dst->ref, &src->ref)) {
        return false;
    }
    dst->type = src->type;
    dst->every = src->every;
    dst->stop = src->stop;
    return true;
}
