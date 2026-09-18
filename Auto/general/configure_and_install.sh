POSTGRES_VERSION="PostgreSQL_master"
PATH_TO_SOURCE_FILES="/home/admin/postgres"
PATH_TO_POSTGRESREPO="/home/admin/PostgresRepo"
PATH_TO_BUILD="${PATH_TO_POSTGRESREPO}/Build/${POSTGRES_VERSION}"

rm -rf "${PATH_TO_BUILD}/"

cd ${PATH_TO_SOURCE_FILES}
git switch master

./configure \
    --enable-debug --enable-cassert --enable-tap-tests \
    CFLAGS="-ggdb -O0 -fno-omit-frame-pointer" CPPFLAGS="-g -O0" \
    --prefix="${PATH_TO_BUILD}"

make -j$(nproc) && make install