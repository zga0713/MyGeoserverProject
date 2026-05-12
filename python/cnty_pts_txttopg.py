# coding=utf-8
import psycopg2
# 连接数据库
conn = psycopg2.connect(database="gis", user="postgres", password="123456", host="127.0.0.1", port="5433")
print('连接成功')
# 建立游标
cur = conn.cursor()
# 建表（如果表已存在则先删除，保证可重复运行）
cur.execute("DROP TABLE IF EXISTS public.v6_time_cnty_pts_utf_wgs84 CASCADE;")
cur.execute('''--建表
CREATE TABLE public. v6_time_cnty_pts_utf_wgs84(
  gid SERIAL8 PRIMARY KEY NOT NULL,
  name_py varchar(40),
  name_ch varchar(45),
  name_ft varchar(45),
  x_coor float8,
  y_coor float8,
  pres_loc varchar(60),
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
  compiler varchar(12),
  gecomplr varchar(10),
  checker varchar(10),
  ent_date varchar(10),
  beg_chg_ty varchar(21),
  end_chg_ty varchar(30),
  geom geometry
);
--建立索引
CREATE INDEX v6_time_cnty_pts_utf_wgs84_index ON v6_time_cnty_pts_utf_wgs84 USING btree(gid);
--表说明
COMMENT ON TABLE public.v6_time_cnty_pts_utf_wgs84 IS '第6版中国历史地理时间序列点数据';
COMMENT ON COLUMN public.v6_time_cnty_pts_utf_wgs84.gid IS '主键ID';
COMMENT ON COLUMN public.v6_time_cnty_pts_utf_wgs84.name_py IS '拼音名称';
COMMENT ON COLUMN public.v6_time_cnty_pts_utf_wgs84.name_ch IS '简体中文名称';
COMMENT ON COLUMN public.v6_time_cnty_pts_utf_wgs84.name_ft IS '繁体中文名称';
COMMENT ON COLUMN public.v6_time_cnty_pts_utf_wgs84.x_coor IS '经度';
COMMENT ON COLUMN public.v6_time_cnty_pts_utf_wgs84.y_coor IS '纬度';
COMMENT ON COLUMN public.v6_time_cnty_pts_utf_wgs84.pres_loc IS '现所在地';
COMMENT ON COLUMN public.v6_time_cnty_pts_utf_wgs84.type_py IS '建制类型拼音';
COMMENT ON COLUMN public.v6_time_cnty_pts_utf_wgs84.type_ch IS '建制类型简体中文';
COMMENT ON COLUMN public.v6_time_cnty_pts_utf_wgs84.lev_rank IS '建制等级';
COMMENT ON COLUMN public.v6_time_cnty_pts_utf_wgs84.beg_yr IS '建制开始时间';
COMMENT ON COLUMN public.v6_time_cnty_pts_utf_wgs84.beg_rule IS '开始时间精度';
COMMENT ON COLUMN public.v6_time_cnty_pts_utf_wgs84.end_yr IS '建制结束时间';
COMMENT ON COLUMN public.v6_time_cnty_pts_utf_wgs84.end_rule IS '结束时间精度';
COMMENT ON COLUMN public.v6_time_cnty_pts_utf_wgs84.note_id IS '系统id';
COMMENT ON COLUMN public.v6_time_cnty_pts_utf_wgs84.obj_type IS 'geometry对象类型';
COMMENT ON COLUMN public.v6_time_cnty_pts_utf_wgs84.sys_id IS '系统id';
COMMENT ON COLUMN public.v6_time_cnty_pts_utf_wgs84.geo_src IS 'geometry数据来源';
COMMENT ON COLUMN public.v6_time_cnty_pts_utf_wgs84.compiler IS '编辑人员';
COMMENT ON COLUMN public.v6_time_cnty_pts_utf_wgs84.gecomplr IS '绘制人员';
COMMENT ON COLUMN public.v6_time_cnty_pts_utf_wgs84.checker IS '审核人员';
COMMENT ON COLUMN public.v6_time_cnty_pts_utf_wgs84.ent_date IS '结束时间';
COMMENT ON COLUMN public.v6_time_cnty_pts_utf_wgs84.beg_chg_ty IS '建制开始原因';
COMMENT ON COLUMN public.v6_time_cnty_pts_utf_wgs84.end_chg_ty IS '建制结束原因';
COMMENT ON COLUMN public.v6_time_cnty_pts_utf_wgs84.geom IS 'geometry对象';''')
# 插入数据
f=open(r'c:\Users\zhou0\Desktop\MyGeoserverProject\data\V6 Time Series County Points\v6_time_cnty_pts_utf_wgs84\v6_time_cnty_pts_utf_wgs84.txt','r',encoding='utf-8')
# 按行读入txt
flines=f.readlines()
for line in flines:
    # 去掉干扰，切词
    abbrlist=line.replace("'"," ").split('\t')
    # name_py,name_ch,name_ft,x_coor,y_coor,pres_loc,type_py,type_ch,lev_rank,beg_yr,beg_rule,end_yr,end_rule,note_id,obj_type,sys_id,geo_src,compiler,gecomplr,checker,ent_date,beg_chg_ty,end_chg_ty,geom
    name_py='null'
    if (abbrlist[0]!=''):
        name_py="'"+abbrlist[0]+"'"
    name_ch='null'
    if (abbrlist[1]!=''):
        name_ch="'"+abbrlist[1]+"'"
    name_ft='null'
    if (abbrlist[2]!=''):
        name_ft="'"+abbrlist[2]+"'"
    x_coor='null'
    if (abbrlist[3]!=''):
        x_coor=abbrlist[3]
    y_coor='null'
    if (abbrlist[4]!=''):
        y_coor=abbrlist[4]
    pres_loc='null'
    if (abbrlist[5]!=''):
        pres_loc="'"+abbrlist[5]+"'"
    type_py='null'
    if (abbrlist[6]!=''):
        type_py="'"+abbrlist[6]+"'"
    type_ch='null'
    if (abbrlist[7]!=''):
        type_ch="'"+abbrlist[7]+"'"
    lev_rank='null'
    if (abbrlist[8]!=''):
        lev_rank="'"+abbrlist[8]+"'"
    beg_yr='null'
    if (abbrlist[9]!=''):
        beg_yr=abbrlist[9]
    beg_rule='null'
    if (abbrlist[10]!=''):
        beg_rule="'"+abbrlist[10]+"'"
    end_yr='null'
    if (abbrlist[11]!=''):
        end_yr=abbrlist[11]
    end_rule='null'
    if (abbrlist[12]!=''):
        end_rule="'"+abbrlist[12]+"'"
    note_id='null'
    if (abbrlist[13]!=''):
        note_id=abbrlist[13]
    obj_type='null'
    if (abbrlist[14]!=''):
        obj_type="'"+abbrlist[14]+"'"
    sys_id='null'
    if (abbrlist[15]!=''):
        sys_id=abbrlist[15]
    geo_src='null'
    if (abbrlist[16]!=''):
        geo_src="'"+abbrlist[16]+"'"
    compiler='null'
    if (abbrlist[17]!=''):
        compiler="'"+abbrlist[17]+"'"
    gecomplr='null'
    if (abbrlist[18]!=''):
        gecomplr="'"+abbrlist[18]+"'"
    checker='null'
    if (abbrlist[19]!=''):
        checker="'"+abbrlist[19]+"'"
    ent_date='null'
    if (abbrlist[20]!=''):
        ent_date="'"+abbrlist[20]+"'"
    beg_chg_ty='null'
    if (abbrlist[21]!=''):
        beg_chg_ty="'"+abbrlist[21]+"'"
    end_chg_ty='null'
    if (abbrlist[22]!=''):
        end_chg_ty="'"+abbrlist[22]+"'"
    geom='null'
    if (abbrlist[23]!=''):
        geom="st_geomfromtext('"+abbrlist[23]+"',4326)"
    # 拼接sql语句
    sqltxt="INSERT INTO v6_time_cnty_pts_utf_wgs84(" \
           "name_py,name_ch,name_ft,x_coor,y_coor,pres_loc,type_py,type_ch,lev_rank,beg_yr,beg_rule," \
           "end_yr,end_rule,note_id,obj_type,sys_id,geo_src,compiler,gecomplr,checker,ent_date," \
           "beg_chg_ty,end_chg_ty,geom) VALUES("+name_py+","+name_ch+","+name_ft+","+x_coor+","+y_coor+","\
           +pres_loc+","+type_py+","+type_ch+","+lev_rank+","+beg_yr+","+beg_rule+","+end_yr+","+end_rule+","\
           +note_id+","+obj_type+","+sys_id+","+geo_src+","+compiler+","+gecomplr+","+checker+","+ent_date+","\
           +beg_chg_ty+","+end_chg_ty+","+geom+")"
    try:
        print(sqltxt)
    except:
        pass
    # 执行sql
    cur.execute(sqltxt)
# 关闭连接
conn.commit()
conn.close()
print('插入完成')