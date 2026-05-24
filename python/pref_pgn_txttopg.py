# coding=utf-8
"""
B1+B2: COPY command + parameterized import for prefecture polygons.
Refactored from row-by-row string-concatenated INSERT to bulk COPY with EWKT geometry.
"""
import psycopg2
from io import StringIO
import time

COLUMNS = (
    'name_py', 'name_ch', 'name_ft', 'x_coor', 'y_coor', 'pres_loc',
    'type_py', 'type_ch', 'lev_rank', 'beg_yr', 'beg_rule', 'end_yr',
    'end_rule', 'note_id', 'obj_type', 'sys_id', 'geo_src', 'compiler',
    'gecomplr', 'checker', 'ent_date', 'beg_chg_ty', 'end_chg_ty', 'geometry',
)

# Numerical columns that should remain as numbers (not quoted strings)
NUM_COLS = {'x_coor', 'y_coor', 'lev_rank', 'beg_yr', 'end_yr', 'note_id', 'sys_id'}


def parse_value(val, col_name):
    """Return cleaned value or None for empty/whitespace-only strings."""
    if val is None or val.strip() == '':
        return None
    v = val.strip()
    if col_name in NUM_COLS:
        try:
            return int(v) if col_name not in ('x_coor', 'y_coor') else float(v)
        except ValueError:
            return v
    return v


def build_wkt(poly_wkt):
    """Build EWKT with SRID=4326 prefix."""
    wkt = poly_wkt.strip()
    if not wkt:
        return None
    if wkt.startswith('SRID='):
        return wkt
    return f'SRID=4326;{wkt}'


def main():
    t0 = time.time()

    conn = psycopg2.connect(
        database='gis', user='postgres', password='123456',
        host='127.0.0.1', port='5433',
    )
    print('[OK] Connected to PostGIS')

    cur = conn.cursor()

    # Drop and recreate table
    cur.execute('DROP TABLE IF EXISTS public.v6_time_pref_pgn_utf_wgs84_geoserver CASCADE;')
    print('[OK] Dropped old table')

    cur.execute('''CREATE TABLE public.v6_time_pref_pgn_utf_wgs84_geoserver (
      gid SERIAL8 PRIMARY KEY NOT NULL,
      name_py varchar(254),
      name_ch varchar(30),
      name_ft varchar(30),
      x_coor float8,
      y_coor float8,
      pres_loc varchar(40),
      type_py varchar(15),
      type_ch varchar(15),
      lev_rank varchar(1),
      beg_yr int8,
      beg_rule varchar(1),
      end_yr int8,
      end_rule varchar(1),
      note_id int8,
      obj_type varchar(7),
      sys_id int8,
      geo_src varchar(10),
      compiler varchar(15),
      gecomplr varchar(15),
      checker varchar(10),
      ent_date varchar(10),
      beg_chg_ty varchar(27),
      end_chg_ty varchar(27),
      geometry geometry(POLYGON,4326) NOT NULL DEFAULT st_geomfromtext('POLYGON((0 0,1 0,1 1,0 1,0 0))', 4326));
    CREATE INDEX idx_pref_pgn_geom_gist ON v6_time_pref_pgn_utf_wgs84_geoserver USING GIST (geometry);
    COMMENT ON TABLE public.v6_time_pref_pgn_utf_wgs84_geoserver IS '第6版中国历史地理时间序列面数据';
    COMMENT ON COLUMN public.v6_time_pref_pgn_utf_wgs84_geoserver.gid IS '主键ID';
    COMMENT ON COLUMN public.v6_time_pref_pgn_utf_wgs84_geoserver.name_py IS '拼音名称';
    COMMENT ON COLUMN public.v6_time_pref_pgn_utf_wgs84_geoserver.name_ch IS '简体中文名称';
    COMMENT ON COLUMN public.v6_time_pref_pgn_utf_wgs84_geoserver.name_ft IS '繁体中文名称';
    COMMENT ON COLUMN public.v6_time_pref_pgn_utf_wgs84_geoserver.x_coor IS '经度';
    COMMENT ON COLUMN public.v6_time_pref_pgn_utf_wgs84_geoserver.y_coor IS '纬度';
    COMMENT ON COLUMN public.v6_time_pref_pgn_utf_wgs84_geoserver.pres_loc IS '现所在地';
    COMMENT ON COLUMN public.v6_time_pref_pgn_utf_wgs84_geoserver.type_py IS '建制类型拼音';
    COMMENT ON COLUMN public.v6_time_pref_pgn_utf_wgs84_geoserver.type_ch IS '建制类型简体中文';
    COMMENT ON COLUMN public.v6_time_pref_pgn_utf_wgs84_geoserver.lev_rank IS '建制等级';
    COMMENT ON COLUMN public.v6_time_pref_pgn_utf_wgs84_geoserver.beg_yr IS '建制开始时间';
    COMMENT ON COLUMN public.v6_time_pref_pgn_utf_wgs84_geoserver.beg_rule IS '开始时间精度';
    COMMENT ON COLUMN public.v6_time_pref_pgn_utf_wgs84_geoserver.end_yr IS '建制结束时间';
    COMMENT ON COLUMN public.v6_time_pref_pgn_utf_wgs84_geoserver.end_rule IS '结束时间精度';
    COMMENT ON COLUMN public.v6_time_pref_pgn_utf_wgs84_geoserver.note_id IS '系统id';
    COMMENT ON COLUMN public.v6_time_pref_pgn_utf_wgs84_geoserver.obj_type IS 'geometry对象类型';
    COMMENT ON COLUMN public.v6_time_pref_pgn_utf_wgs84_geoserver.sys_id IS '系统id';
    COMMENT ON COLUMN public.v6_time_pref_pgn_utf_wgs84_geoserver.geo_src IS 'geometry数据来源';
    COMMENT ON COLUMN public.v6_time_pref_pgn_utf_wgs84_geoserver.compiler IS '编辑人员';
    COMMENT ON COLUMN public.v6_time_pref_pgn_utf_wgs84_geoserver.gecomplr IS '绘制人员';
    COMMENT ON COLUMN public.v6_time_pref_pgn_utf_wgs84_geoserver.checker IS '审核人员';
    COMMENT ON COLUMN public.v6_time_pref_pgn_utf_wgs84_geoserver.ent_date IS '结束时间';
    COMMENT ON COLUMN public.v6_time_pref_pgn_utf_wgs84_geoserver.beg_chg_ty IS '建制开始原因';
    COMMENT ON COLUMN public.v6_time_pref_pgn_utf_wgs84_geoserver.end_chg_ty IS '建制结束原因';
    COMMENT ON COLUMN public.v6_time_pref_pgn_utf_wgs84_geoserver.geometry IS 'geometry数据';''')
    print('[OK] Created table with GIST index')

    # Parse source data
    src_path = r'c:\Users\zhou0\Desktop\MyGeoserverProject\data\V6 Time Series Prefecture Polygons\v6_time_pref_pgn_utf_wgs84\v6_time_pref_pgn_utf_wgs84.txt'
    with open(src_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print(f'[..] Parsing {len(lines)} source lines...')

    buffer = StringIO()
    row_count = 0
    col_names = (
        'name_py', 'name_ch', 'name_ft', 'x_coor', 'y_coor', 'pres_loc',
        'type_py', 'type_ch', 'lev_rank', 'beg_yr', 'beg_rule', 'end_yr',
        'end_rule', 'note_id', 'obj_type', 'sys_id', 'geo_src', 'compiler',
        'gecomplr', 'checker', 'ent_date', 'beg_chg_ty', 'end_chg_ty',
    )

    for line in lines:
        fields = line.rstrip('\n').split('\t')
        if len(fields) < 24:
            continue

        # Parse attributes (columns 0-22)
        row_values = []
        for i, col_name in enumerate(col_names):
            row_values.append(parse_value(fields[i], col_name))

        geom_wkt = fields[23] if len(fields) > 23 else ''

        if not geom_wkt:
            continue

        if 'MULTI' in geom_wkt:
            # Decompose MULTIPOLYGON into individual POLYGON rows
            inner = geom_wkt.replace('MULTIPOLYGON (((', '').replace(')))', '')
            parts = inner.split(')),((')
            for poly in parts:
                wkt = build_wkt(f'POLYGON (({poly}))')
                row_data = row_values + [wkt]
                buffer.write('\t'.join(
                    '\\N' if v is None else str(v) for v in row_data
                ) + '\n')
                row_count += 1
        else:
            wkt = build_wkt(geom_wkt)
            row_data = row_values + [wkt]
            buffer.write('\t'.join(
                '\\N' if v is None else str(v) for v in row_data
            ) + '\n')
            row_count += 1

    print(f'[..] Prepared {row_count} rows for COPY')

    # Bulk insert via COPY
    buffer.seek(0)
    cur.copy_from(
        buffer,
        'v6_time_pref_pgn_utf_wgs84_geoserver',
        sep='\t',
        null='\\N',
        columns=COLUMNS,
    )
    conn.commit()
    elapsed = time.time() - t0
    print(f'[OK] COPY {row_count} rows in {elapsed:.2f}s')

    # Verify
    cur.execute('SELECT COUNT(*) FROM v6_time_pref_pgn_utf_wgs84_geoserver;')
    count = cur.fetchone()[0]
    print(f'[OK] Table has {count} rows')

    conn.close()
    print('[OK] Done')


if __name__ == '__main__':
    main()
