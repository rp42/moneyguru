#include "currency.h"

typedef struct {
    Currency *default_currency;
    int first_weekday;
    int ahead_months;
    int year_start_month;
} DocumentProperties;
