#include "transaction.h"
#include "recurrence.h"

typedef struct {
    Transaction ref;
    // date at which the schedule stops. 0 if never.
    time_t stop;
    RepeatType type;
    // Repeats every X units of `type`.
    unsigned int every;
} Schedule;

// ref is copied, not kept as a pointer.
void
schedule_init(
    Schedule *sched,
    const Transaction *ref,
    RepeatType type,
    unsigned int every);

bool
schedule_copy(Schedule *dst, const Schedule *src);
