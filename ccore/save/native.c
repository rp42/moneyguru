#include <stdio.h>
#include <glib.h>
#include "../save.h"

static char*
escape_newline(char *s)
{
    char **toks = g_strsplit(s, "\n", 0);
    char *res = g_strjoinv("\\n", toks);
    g_strfreev(toks);
    return res;
}

static void
setattrib(FILE *fp, char *fmt, char *val)
{
    if (val) {
        char *s = g_markup_printf_escaped(fmt, val);
        fwrite(s, strlen(s), 1, fp);
        g_free(s);
    }
}

static int
date2str(char *dest, time_t date)
{
    struct tm *t = localtime(&date);
    return sprintf(
        dest, "%d-%02d-%02d", t->tm_year+1900, t->tm_mon+1, t->tm_mday);
}

static void
writedate(FILE *fp, char *fmt, time_t val)
{
    if (val) {
        char dfmt[20];
        date2str(dfmt, val);
        char *s = g_markup_printf_escaped(fmt, dfmt);
        fwrite(s, strlen(s), 1, fp);
        g_free(s);
    }
}

static int
write_txn(FILE *fp, Transaction *t)
{
    char dfmt[20];
    date2str(dfmt, t->date);
    char *s = g_markup_printf_escaped(
        "<transaction date=\"%s\" mtime=\"%ld\"",
        dfmt,
        t->mtime);
    fwrite(s, strlen(s), 1, fp);
    g_free(s);
    setattrib(fp, " description=\"%s\"", t->description);
    setattrib(fp, " payee=\"%s\"", t->payee);
    setattrib(fp, " checkno=\"%s\"", t->checkno);
    if (t->notes) {
        char *notes = escape_newline(t->notes);
        setattrib(fp, " notes=\"%s\"", notes);
        g_free(notes);
    }
    s = ">\n";
    fwrite(s, strlen(s), 1, fp);

    for (int i=0; i<t->splitcount; i++) {
        Split *sp = &t->splits[i];
        char afmt[64];
        if (!amount_format(afmt, &sp->amount, true, false)) {
            return -2;
        }
        char *aname = "";
        if (sp->account) {
            aname = sp->account->name;
        }
        s = g_markup_printf_escaped(
            "<split account=\"%s\" amount=\"%s\"",
            aname,
            afmt);
        fwrite(s, strlen(s), 1, fp);
        g_free(s);
        setattrib(fp, " memo=\"%s\"", sp->memo);
        setattrib(fp, " reference=\"%s\"", sp->reference);
        writedate(fp, " reconciliation_date=\"%s\"", sp->reconciliation_date);
        s = " />\n";
        fwrite(s, strlen(s), 1, fp);
    }

    s = "</transaction>\n";
    fwrite(s, strlen(s), 1, fp);
    return 0;
}

int
save_native(
    char *filename,
    char *document_id,
    DocumentProperties *properties,
    AccountList *accounts,
    TransactionList *transactions,
    Schedule **schedules)
{
    FILE *fp = fopen(filename, "w");
    if (fp == NULL) {
        return -1;
    }
    char *s;

    s = g_markup_printf_escaped(
        "<moneyguru-file document_id=\"%s\">\n",
        document_id);
    fwrite(s, strlen(s), 1, fp);
    g_free(s);

    s = g_markup_printf_escaped(
        "<properties default_currency=\"%s\" first_weekday=\"%d\""
        " ahead_months=\"%d\" year_start_month=\"%d\"/>\n",
        properties->default_currency->code,
        properties->first_weekday,
        properties->ahead_months,
        properties->year_start_month);
    fwrite(s, strlen(s), 1, fp);
    g_free(s);

    for (int i=0; i<accounts->count; i++) {
        Account *a = accounts->accounts[i];
        s = g_markup_printf_escaped(
            "<account name=\"%s\" currency=\"%s\" type=\"%s\"",
            a->name,
            a->currency->code,
            account_type_name(a));
        fwrite(s, strlen(s), 1, fp);
        g_free(s);
        setattrib(fp, " group=\"%s\"", a->groupname);
        setattrib(fp, " reference=\"%s\"", a->reference);
        setattrib(fp, " account_number=\"%s\"", a->account_number);
        if (a->inactive) {
            s = " inactive=\"y\"";
            fwrite(s, strlen(s), 1, fp);
        }
        if (a->notes) {
            char *notes = escape_newline(a->notes);
            setattrib(fp, " notes=\"%s\"", notes);
            g_free(notes);
        }
        fwrite(" />\n", 4, 1, fp);
    }

    for (int i=0; i<transactions->count; i++) {
        Transaction *t = transactions->txns[i];
        int res = write_txn(fp, t);
        if (res != 0) {
            return res;
        }
    }

    while (*schedules) {
        Schedule *sc = *schedules;
        if (!schedule_is_alive(sc)) {
            continue;
        }
        s = g_markup_printf_escaped(
            "<recurrence type=\"%s\" every=\"%d\"",
            repeat_type_name(sc->type),
            sc->every);
        fwrite(s, strlen(s), 1, fp);
        g_free(s);
        writedate(fp, " stop=\"%s\"", sc->stop);
        s = ">\n";
        fwrite(s, strlen(s), 1, fp);
        write_txn(fp, &sc->ref);

        GHashTableIter iter;
        gpointer key, value;
        g_hash_table_iter_init(&iter, sc->deletions);
        while (g_hash_table_iter_next(&iter, &key, &value)) {
            writedate(fp, "<exception date=\"%s\" />\n", (time_t)key);
        }

        g_hash_table_iter_init(&iter, sc->globalchanges);
        while (g_hash_table_iter_next(&iter, &key, &value)) {
            writedate(fp, "<change date=\"%s\">\n", (time_t)key);
            write_txn(fp, (Transaction *)value);
            s = "</change>\n";
            fwrite(s, strlen(s), 1, fp);
        }
        s = "</recurrence>\n";
        fwrite(s, strlen(s), 1, fp);
        schedules++;
    }
    s = "</moneyguru-file>";
    fwrite(s, strlen(s), 1, fp);
    fclose(fp);
    return 0;
}
