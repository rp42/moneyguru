#include "transaction.h"
#include "recurrence.h"

typedef struct {
    Transaction ref;
    // date at which the schedule stops. 0 if never.
    time_t stop;
    RepeatType type;
    // Repeats every X units of `type`.
    int every;
} Schedule;

