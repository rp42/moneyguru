#include <time.h>

#define SECS_IN_DAY 86400

typedef enum {
    REPEAT_DAILY = 1,
    REPEAT_WEEKLY = 2,
    REPEAT_MONTHLY = 3,
    REPEAT_YEARLY = 4,
    REPEAT_WEEKDAY = 5,
    REPEAT_WEEKDAY_LAST = 6,
} RepeatType;

/* Increment `date` by `count` units of `repeat_type`.
 *
 * `count` can be negative.
 *
 * When given a valid `date`, this function almost always succeeds. The only
 * case where it doesn't is in REPEAT_WEEKDAY if when asking for the 5th week.
 *
 * REPEAT_DAILY: increment by X days
 * REPEAT_WEEKLY: increment by X weeks
 * REPEAT_MONTHLY: increment by X months. If the day doesn't exist (31st or
 *                 February), returns the last day of the target month.
 * REPEAT_YEARLY: increment by X years. If the day doesn't exist (29th of
 *                February), returns the 28th.
 * REPEAT_WEEKLY: increment by X months, but anchors to weekno/day of week.
 *                Example: 2nd friday of October -> 2nd friday of November.
 * REPEAT_WEEKDAY_LAST: Like REPEAT_WEEKLY, but for "last day X (friday) of
 *                      the month".
 *
 * Returns -1 on error.
 */
time_t
inc_date(time_t date, RepeatType repeat_type, int count);

/* Calls inc_date and "skips" invalid dates
 *
 * When inc_date returns an invalid date (possible in some monthly and weekly
 * situations), it "skips" the date and returns the next one, with the same
 * repeat_type and count.
 *
 * Also returns -1 on error, but this time, if you get -1, something is really
 * wrong.
 */
time_t
inc_date_skip(time_t date, RepeatType repeat_type, int count);

/* Return repeat type under its string form ("daily", "monthly", etc.).
 */ 
char*
repeat_type_name(RepeatType t);
