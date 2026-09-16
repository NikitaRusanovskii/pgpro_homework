#include "postgres.h"
#include "fmgr.h"
#include "varatt.h"

PG_MODULE_MAGIC;

void _PG_init(void);
void _PG_fini(void);

void _PG_init(void) {} // при загрузке расширения
void _PG_fini(void) {} // при выгрузке расширения

PG_FUNCTION_INFO_V1(change_text);
Datum change_text(PG_FUNCTION_ARGS) {
    text* dt = PG_GETARG_TEXT_PP(0); // запакованная varlena
    char symbol = PG_GETARG_CHAR(1);
    int32 len = VARSIZE_ANY_EXHDR(dt);
    text* new_dt = (text*)palloc(VARSIZE_ANY_EXHDR(dt) + VARHDRSZ);
    SET_VARSIZE(new_dt, VARSIZE_ANY_EXHDR(dt) + VARHDRSZ);
    for(int32 i = 0; i < len; i++) {
        VARDATA_ANY(new_dt)[i] = VARDATA_ANY(dt)[i] ^ symbol;
    }
    PG_RETURN_TEXT_P(new_dt);
}
