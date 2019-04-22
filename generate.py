import os
import re
import shutil
import zipfile
import pymysql

db_user = 'root'

db_password = 'mysql'

package_path = 'com.simbook'

db_name = package_path.split('.')[-1]
db_name_cap = db_name.capitalize()

sep = os.sep

print('数据库账号: {}'.format(db_user))
print('数据库密码: {}'.format(db_password))
print('数据库名: {}'.format(db_name))
print('包名: {}'.format(package_path))

# 删除旧文件
if os.path.exists('demo'):
    shutil.rmtree('demo')
if os.path.exists(db_name_cap):
    shutil.rmtree(db_name_cap)

# 解压data.zip
f = zipfile.ZipFile("demo.zip", 'r')
for file in f.namelist():
    f.extract(file)

os.rename('demo{}demo.iml'.format(sep),
          'demo{}{}.iml'.format(sep, db_name_cap))

with open('demo{sep}src{sep}main{sep}resources{sep}spring-mvc.xml'.format(sep=sep), 'r',
          encoding='utf-8') as f:
    content = f.read()
    with open('demo{sep}src{sep}main{sep}resources{sep}spring-mvc.xml'.format(sep=sep), 'w',
              encoding='utf-8') as f:
        f.write(content.replace('com.demo', package_path))

with open('demo{sep}src{sep}main{sep}resources{sep}jdbc.properties'.format(sep=sep), 'w', encoding='utf-8') as f:
    jdbc_content = '''
driver=com.mysql.jdbc.Driver
url=jdbc:mysql://localhost:3306/{db_name}?useUnicode=true&characterEncoding=utf-8
username={db_user}
password={db_password}
#定义初始连接数
initialSize=0
#定义最大连接数
maxActive=20
#定义最大空闲
maxIdle=20
#定义最小空闲
minIdle=1
#定义最长等待时间
maxWait=60000
'''.format(db_name=db_name, db_user=db_user, db_password=db_password)
    f.write(jdbc_content)

with open('demo{sep}src{sep}main{sep}resources{sep}spring-mybatis.xml'.format(sep=sep), 'r', encoding='utf-8') as f:
    mybatis_content = f.read()
    mybatis_content = mybatis_content.replace("com.demo", package_path)
    mybatis_content = mybatis_content.replace("com/demo", package_path.replace('.', '/'))
    with open('demo{sep}src{sep}main{sep}resources{sep}spring-mybatis.xml'.format(sep=sep), 'w', encoding='utf-8') as f:
        f.write(mybatis_content)

with open('demo{sep}src{sep}main{sep}resources{sep}spring-mvc.xml'.format(sep=sep), 'r', encoding='utf-8') as f:
    spring_mvc = f.read()
    spring_mvc = spring_mvc.replace("com.demo", package_path)
    with open('demo{sep}src{sep}main{sep}resources{sep}spring-mvc.xml'.format(sep=sep), 'w', encoding='utf-8') as f:
        f.write(spring_mvc)

with open('demo{sep}src{sep}main{sep}webapp{sep}WEB-INF{sep}web.xml'.format(sep=sep), 'r', encoding='utf-8') as f:
    web = f.read()
    web = web.replace("Demo", db_name_cap)
    with open('demo{sep}src{sep}main{sep}webapp{sep}WEB-INF{sep}web.xml'.format(sep=sep), 'w', encoding='utf-8') as f:
        f.write(web)

with open('demo{sep}pom.xml'.format(sep=sep), 'r', encoding='utf-8') as f:
    web = f.read()
    web = web.replace("<groupId>com</groupId>", "<groupId>{}</groupId>".format('.'.join(package_path.split('.')[:-1:])))
    web = web.replace("demo", db_name)
    web = web.replace("<finalName>demo</finalName>", "<finalName>{}</finalName>".format(db_name))
    with open('demo{sep}pom.xml'.format(sep=sep), 'w', encoding='utf-8') as f:
        f.write(web)

os.rename('demo', db_name_cap)

# 创建文件夹
base_path = db_name + '{sep}src{sep}main{sep}java{sep}'.format(sep=sep)
for _dir in package_path.split('.'):
    base_path += _dir + sep
    if not os.path.exists(base_path):
        os.mkdir(base_path)

dir_name_list = ['controller', 'dao', 'filter', 'interceptor', 'mapping', 'service', 'service{sep}impl'.format(sep=sep), 'pojo', 'util']
for dir_name in dir_name_list:
    if not os.path.exists(base_path + dir_name):
        os.mkdir(base_path + dir_name)

replace_name_list = [
    'data{sep}controller{sep}UserExampleController.java'.format(sep=sep),
    'data{sep}dao{sep}UserExampleDAO.java'.format(sep=sep),
    'data{sep}filter{sep}LoginFilter.java'.format(sep=sep),
    'data{sep}interceptor{sep}LoginInterceptor.java'.format(sep=sep),
    'data{sep}interceptor{sep}LoginInterceptor.java'.format(sep=sep),
    'data{sep}mapping{sep}UserExampleMapper.xml'.format(sep=sep),
    'data{sep}pojo{sep}UserExample.java'.format(sep=sep),
    'data{sep}service{sep}UserExampleService.java'.format(sep=sep),
    'data{sep}service{sep}impl{sep}UserExampleServiceImpl.java'.format(sep=sep),
    'data{sep}util{sep}WXBizDataCrypt.java'.format(sep=sep),
    'data{sep}util{sep}HTTP.java'.format(sep=sep),

]
for replace_name in replace_name_list:
    with open(db_name + sep + replace_name, 'r',
              encoding='utf-8') as f:
        content = f.read()
        with open(base_path.capitalize() + replace_name[5::], 'w',
                  encoding='utf-8') as f:
            f.write(content.replace('com.demo', package_path))

shutil.rmtree(db_name + sep + 'data')

# 从数据库中获取数据
db = pymysql.connect("localhost", db_user, db_password, db_name)
cursor = db.cursor()

# 删除示例 userexample 表
sql = '''DROP TABLE IF EXISTS `userexample`;'''
cursor.execute(sql)
db.commit()

cursor.execute("show tables")

tables = cursor.fetchall()
for table in tables:
    table_name = table[0]
    table_name_cap = table_name.capitalize()
    print()
    print('表名:', table_name)
    properties_name_type = []
    # 获取外键
    cursor.execute("show create table " + table_name + ';')
    result = cursor.fetchone()
    fk_properties = re.findall('FOREIGN KEY \(`.*?`\) REFERENCES `(.*?)`', result[1])

    cursor.execute("describe " + table_name + ';')
    is_exist_date = False
    for row in cursor.fetchall():
        _name = row[0]
        _type = row[1]
        name_type = []
        _name = _name.split('_')[1]
        if _name in fk_properties:
            name_type = [_name, _name.capitalize()]
        elif 'int' in _type:
            name_type = [_name, 'Integer']
        elif 'date' in _type:
            name_type = [_name, 'Date']
            is_exist_date = True
        else:
            name_type = [_name, 'String']
        properties_name_type.append(name_type)
    # pojo
    print('提示：为{}构建pojo'.format(table_name))
    pojo_template = '''package {package_path}.pojo;\n\nimport java.util.Map;\n'''
    if is_exist_date:
        pojo_template += '''import java.util.Date;\n\n'''

    for fk_property in fk_properties:
        pojo_template += '''import {}.pojo.{};\n'''.format(package_path, fk_property.capitalize())
    pojo_template += '''
public class {table_name_cap} 左

{attributes}

\tpublic {table_name_cap}() 左右
\t// 在controller中调用，传进 参数map 以获得{table_name_cap}实例
\tpublic {table_name_cap}(Map<String, Object> map) 左
\t\t// this.id = (String)map.get("id");\n\t\t'''

    pojo_template += '\n\t\t'.join(['this.{} = ({})map.get("{}");'.format(_name, _type.capitalize(), _name) for _name, _type in properties_name_type])

    pojo_template += '''
\t右
\t{gets}\t{sets}
右
'''
    pojo_get_template = '''
\tpublic {class_type} get{class_name_cap}() 左
\t\treturn {class_name_lower};
\t右
'''

    pojo_set_template = '''
\tpublic void set{class_name_cap}({class_type} {class_name_lower}) 左
\t\tthis.{class_name_lower} = {class_name_lower};
\t右'''
    attributes = '\n'.join(['\tprivate {} {};'.format(_type, _name) for _name, _type in properties_name_type])
    gets = ''.join([
                       pojo_get_template.format(
                           class_type=_type,
                           class_name_cap=_name.capitalize(),
                           class_name_lower=_name
                       ) for _name, _type in properties_name_type])
    sets = ''.join([
                       pojo_set_template.format(
                           class_type=_type,
                           class_name_cap=_name.capitalize(),
                           class_name_lower=_name
                       ) for _name, _type in properties_name_type])
    pojo_str = pojo_template.format(package_path=package_path,
                                    table_name_cap=table_name_cap,
                                    attributes=attributes,
                                    gets=gets,
                                    sets=sets)
    with open(base_path + 'pojo' + sep + '{}.java'.format(table_name_cap), 'w', encoding='utf-8') as f:
        f.write(pojo_str.replace('左', '{').replace('右', '}'))

    # DAO
    print('提示：为{}构建DAO'.format(table_name))
    dao_template = '''package {package_path}.dao;\n\n'''
    for fk in fk_properties:
        dao_template += '''import {}.pojo.{};\n'''.format(package_path, fk.capitalize())
    dao_template += '''import {package_path}.pojo.{class_name_cap};

import org.apache.ibatis.annotations.Param;
import org.springframework.stereotype.Repository;

import java.util.List;\n'''

    dao_template += '''

@Repository
public interface {class_name_cap}DAO 左

\tvoid add{class_name_cap}(@Param("{class_name_lower}") {class_name_cap} {class_name_lower});

\tvoid update{class_name_cap}(@Param("{class_name_lower}") {class_name_cap} {class_name_lower});

\tvoid delete{class_name_cap}(@Param("{class_name_lower}") {class_name_cap} {class_name_lower});

\tvoid delete{class_name_cap}ById(@Param("{class_name_lower}Id") String {class_name_lower}Id);

\t{class_name_cap} get{class_name_cap}(@Param("{class_name_lower}") {class_name_cap} {class_name_lower});

\t{class_name_cap} get{class_name_cap}ById(@Param("{class_name_lower}Id") String {class_name_lower}Id);

\tList<{class_name_cap}> getAll{class_name_cap}s();
'''
    # 单个外键查删
    for fk_property in fk_properties:
        dao_template += '''
\t{class_name_cap} get{class_name_cap}By{fk_property_cap}(@Param("{fk_property_lower}") {fk_property_cap} {fk_property_lower});\n
\tList<{class_name_cap}> get{class_name_cap}sBy{fk_property_cap}(@Param("{fk_property_lower}") {fk_property_cap} {fk_property_lower});\n
\tvoid delete{class_name_cap}By{fk_property_cap}(@Param("{fk_property_lower}") {fk_property_cap} {fk_property_lower});\n
\tvoid delete{class_name_cap}sBy{fk_property_cap}(@Param("{fk_property_lower}") {fk_property_cap} {fk_property_lower});
'''.format(fk_property_lower=fk_property.lower(),
           fk_property_cap=fk_property.capitalize(),
            package_path=package_path,
            class_name_cap=table_name_cap,
            class_name_lower=table_name.lower())
    # 联合外键查删
    dao_template += ''''
\t{class_name_cap} get{class_name_cap}By{fk_properties}({fk_properties_param});\n
\tList<{class_name_cap}> get{class_name_cap}sBy{fk_properties}({fk_properties_param});\n
\tvoid delete{class_name_cap}By{fk_properties}({fk_properties_param});\n
\tvoid delete{class_name_cap}sBy{fk_properties}({fk_properties_param});
'''.format(fk_properties='And'.join([fk_property.capitalize()+'Id' for fk_property in fk_properties]),
           fk_properties_param=', '.join(['@Param("{fk_property_lower}Id") Integer {fk_property_lower}Id'.format(fk_property_cap=fk_property.capitalize(),
                                                                                                       fk_property_lower=fk_property.lower())
                                          for fk_property in fk_properties]),
            package_path=package_path,
            class_name_cap=table_name_cap,
            class_name_lower=table_name.lower())

    dao_template += '\n右\n'
    dao_str = dao_template.format(
        package_path=package_path,
        class_name_cap=table_name_cap,
        class_name_lower=table_name.lower())

    with open(base_path + 'dao' + os.sep + '{}DAO.java'.format(table_name_cap), 'w', encoding='utf-8') as f:
        f.write(dao_str.replace('左', '{').replace('右', '}'))

    # service
    print('提示：为{}构建service'.format(table_name))

    service_template = '''package {package_path}.service;\n
'''
    for fk in fk_properties:
        service_template += '''import {}.pojo.{};\n'''.format(package_path, fk.capitalize())
    service_template += '''import {package_path}.pojo.{class_name_cap};

import java.util.List;

public interface {class_name_cap}Service 左

\tvoid add{class_name_cap}({class_name_cap} {class_name_lower});

\tvoid update{class_name_cap}({class_name_cap} {class_name_lower});

\tvoid delete{class_name_cap}({class_name_cap} {class_name_lower});

\tvoid delete{class_name_cap}ById(String {class_name_lower}Id);

\t{class_name_cap} get{class_name_cap}({class_name_cap} {class_name_lower});

\t{class_name_cap} get{class_name_cap}ById(String {class_name_lower}Id);

\tList<{class_name_cap}> getAll{class_name_cap}s();
'''
    # 单个外键查删
    for fk_property in fk_properties:
        service_template += '''
\t{class_name_cap} get{class_name_cap}By{fk_property_cap}({fk_property_cap} {fk_property_lower});\n
\tList<{class_name_cap}> get{class_name_cap}sBy{fk_property_cap}({fk_property_cap} {fk_property_lower});\n
\tvoid delete{class_name_cap}By{fk_property_cap}({fk_property_cap} {fk_property_lower});\n
\tvoid delete{class_name_cap}sBy{fk_property_cap}({fk_property_cap} {fk_property_lower});
'''.format(fk_property_lower=fk_property.lower(),
           fk_property_cap=fk_property.capitalize(),
            package_path=package_path,
            class_name_cap=table_name_cap,
            class_name_lower=table_name.lower())
    # 联合外键查删
    service_template += ''''
\t{class_name_cap} get{class_name_cap}By{fk_properties}({fk_properties_param});\n
\tList<{class_name_cap}> get{class_name_cap}sBy{fk_properties}({fk_properties_param});\n
\tvoid delete{class_name_cap}By{fk_properties}({fk_properties_param});\n
\tvoid delete{class_name_cap}sBy{fk_properties}({fk_properties_param});
'''.format(fk_properties='And'.join([fk_property.capitalize()+'Id' for fk_property in fk_properties]),
           fk_properties_param=', '.join(['Integer {fk_property_lower}Id'.format(fk_property_cap=fk_property.capitalize(),
                                                                                                       fk_property_lower=fk_property.lower())
                                          for fk_property in fk_properties]),
            package_path=package_path,
            class_name_cap=table_name_cap,
            class_name_lower=table_name.lower())

    service_template+= '\n右'
    service_str = service_template.format(
        package_path=package_path,
        class_name_cap=table_name_cap,
        class_name_lower=table_name.lower())
    with open(base_path + 'service' + os.sep + '{}Service.java'.format(table_name_cap), 'w',
              encoding='utf-8') as f:
        f.write(service_str.replace('左', '{').replace('右', '}'))

    # serviceImpl
    print('提示：为{}构建serviceImpl'.format(table_name))
    serviceImpl_template = '''package {package_path}.service.impl;

import {package_path}.dao.{class_name_cap}DAO;
import {package_path}.pojo.{class_name_cap};'''
    
    for fk in fk_properties:
        serviceImpl_template += '''import {}.pojo.{};\n'''.format(package_path, fk.capitalize())
    serviceImpl_template += '''import {package_path}.pojo.{class_name_cap};\n'''

    serviceImpl_template += '''import {package_path}.service.{class_name_cap}Service;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service("{class_name_lower}Service")
public class {class_name_cap}ServiceImpl implements {class_name_cap}Service 左

\t@Autowired
\tprivate {class_name_cap}DAO {class_name_lower}DAO;

\tpublic void add{class_name_cap}({class_name_cap} {class_name_lower}) 左
\t\t{class_name_lower}DAO.add{class_name_cap}({class_name_lower});
\t右

\tpublic void update{class_name_cap}({class_name_cap} {class_name_lower}) 左
\t\t{class_name_lower}DAO.update{class_name_cap}({class_name_lower});
\t右

\tpublic void delete{class_name_cap}({class_name_cap} {class_name_lower}) 左
\t\t{class_name_lower}DAO.delete{class_name_cap}({class_name_lower});
\t右
    
\tpublic void delete{class_name_cap}ById(String {class_name_lower}Id) 左
\t\t{class_name_lower}DAO.delete{class_name_cap}ById({class_name_lower}Id);
\t右
    
\tpublic {class_name_cap} get{class_name_cap}({class_name_cap} {class_name_lower}) 左
\t\treturn {class_name_lower}DAO.get{class_name_cap}({class_name_lower});
\t右
    
\tpublic {class_name_cap} get{class_name_cap}ById(String {class_name_lower}Id) 左
\t\treturn {class_name_lower}DAO.get{class_name_cap}ById({class_name_lower}Id);
\t右

\tpublic List<{class_name_cap}> getAll{class_name_cap}s() 左
\t\treturn {class_name_lower}DAO.getAll{class_name_cap}s();
\t右
'''
    # 单个外键查删
    for fk_property in fk_properties:
        serviceImpl_template += '''
\tpublic {class_name_cap} get{class_name_cap}By{fk_property_cap}({fk_property_cap} {fk_property_lower}) 左
\t\treturn {class_name_lower}DAO.get{class_name_cap}By{fk_property_cap}({fk_property_lower});
\t右

\tpublic List<{class_name_cap}> get{class_name_cap}sBy{fk_property_cap}({fk_property_cap} {fk_property_lower}) 左
\t\treturn {class_name_lower}DAO.get{class_name_cap}sBy{fk_property_cap}({fk_property_lower});
\t右

\tpublic void delete{class_name_cap}By{fk_property_cap}({fk_property_cap} {fk_property_lower}) 左
\t\t{class_name_lower}DAO.get{class_name_cap}By{fk_property_cap}({fk_property_lower});
\t右

\tpublic void delete{class_name_cap}sBy{fk_property_cap}({fk_property_cap} {fk_property_lower}) 左
\t\t{class_name_lower}DAO.get{class_name_cap}sBy{fk_property_cap}({fk_property_lower});
\t右
'''.format(fk_property_lower=fk_property.lower(),
           fk_property_cap=fk_property.capitalize(),
            package_path=package_path,
            class_name_cap=table_name_cap,
            class_name_lower=table_name.lower())

    
    # 联合外键查删
    serviceImpl_template += ''''
\tpublic {class_name_cap} get{class_name_cap}By{fk_properties}({fk_properties_param}) 左
\t\treturn {class_name_lower}DAO.get{class_name_cap}By{fk_properties}({fk_properties_param_inner});
\t右

\tpublic List<{class_name_cap}> get{class_name_cap}sBy{fk_properties}({fk_properties_param}) 左
\t\treturn {class_name_lower}DAO.get{class_name_cap}sBy{fk_properties}({fk_properties_param_inner});
\t右

\tpublic void delete{class_name_cap}By{fk_properties}({fk_properties_param}) 左
\t\t{class_name_lower}DAO.delete{class_name_cap}By{fk_properties}({fk_properties_param_inner});
\t右

\tpublic void delete{class_name_cap}sBy{fk_properties}({fk_properties_param}) 左
\t\t{class_name_lower}DAO.delete{class_name_cap}sBy{fk_properties}({fk_properties_param_inner});
\t右
'''.format(fk_properties='And'.join([fk_property.capitalize()+'Id' for fk_property in fk_properties]),
           fk_properties_param=', '.join(['Integer {fk_property_lower}Id'.format(fk_property_cap=fk_property.capitalize(),
                                                                                                       fk_property_lower=fk_property.lower())
                                          for fk_property in fk_properties]),
           fk_properties_param_inner=', '.join(['{fk_property_lower}Id'.format(fk_property_cap=fk_property.capitalize(),
                                                                                                       fk_property_lower=fk_property.lower())
                                          for fk_property in fk_properties]),
            package_path=package_path,
            class_name_cap=table_name_cap,
            class_name_lower=table_name.lower())

    serviceImpl_template+= '\n右'

    serviceImpl_str = serviceImpl_template.format(
        package_path=package_path,
        class_name_cap=table_name_cap,
        class_name_lower=table_name.lower())
    with open(base_path + 'service' + os.sep + 'impl' + os.sep + '{}ServiceImpl.java'.format(table_name_cap),
              'w', encoding='utf-8') as f:
        f.write(serviceImpl_str.replace('左', '{').replace('右', '}'))

    # controller
    print('提示：为{}构建controller'.format(table_name))
    controller_template = '''package {package_path}.controller;\n
import {package_path}.pojo.User;\n'''
    if table_name != 'User':
        controller_template += '''import {package_path}.pojo.{class_name_cap};\n'''

    controller_template += '''
import {package_path}.service.{class_name_cap}Service;
import {package_path}.service.UserService;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;

import com.alibaba.fastjson.JSON;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Controller
public class {class_name_cap}Controller 左
\t@Autowired
\tprivate UserService userService;
'''
    if table_name != 'user':
        controller_template += '''\t@Autowired\n\tprivate {class_name_cap}Service {class_name_lower}Service;'''
    controller_template += '''
{tojson}
{req}
右
'''
    tojson_template = '''
\tprivate HashMap toMap({class_name_cap} {class_name_lower}) 左
\t\tHashMap hashMap = new HashMap();
{hashMap_put}
\t\treturn hashMap;
\t右

\tprivate HashMap[] toMapArray(List<{class_name_cap}> {class_name_lower}List) 左
\t\tHashMap[] hashMaps = new HashMap[{class_name_lower}List.size()];
\t\tfor (int index = 0; index < {class_name_lower}List.size(); index++) 左
\t\t\t{class_name_cap} {class_name_lower} = {class_name_lower}List.get(index);
\t\t\thashMaps[index] = new HashMap();
{hashMaps_put}
\t\t右
\t\treturn hashMaps;
\t右
'''
    hashMap_put = '\n'.join([
                                '\t\thashMap.put("{class_name_lower}", {table_name}.get{class_name_cap}());'.format(
                                    table_name=table_name.lower(),
                                    class_name_lower=_name.lower(),
                                    class_name_cap=_name.capitalize())
                                for _name, _type in properties_name_type
                                ])
    hashMaps_put = '\n'.join([
                                 '\t\t\thashMaps[index].put("{class_name_lower}", {table_name}.get{class_name_cap}());'.format(
                                     table_name=table_name.lower(),
                                     class_name_lower=_name.lower(),
                                     class_name_cap=_name.capitalize())
                                 for _name, _type in properties_name_type
                                 ])
    tojson_str = tojson_template.format(
        hashMap_put=hashMap_put,
        hashMaps_put=hashMaps_put,
        class_name_lower=table_name.lower(),
        class_name_cap=table_name_cap,
    )

    req_template = '''
\t@RequestMapping(value = "api/{class_name_lower}/add{class_name_cap}")
\t@ResponseBody // 添加{class_name_cap}
\tpublic void add{class_name_cap}(@CookieValue("JSESSIONID") String JSESSIONID, @RequestBody Map<String, Object> map) 左
\t\t//User user = userService.getUserByJSESSIONID(JSESSIONID);
\t\t{class_name_cap} {class_name_lower} = new {class_name_cap}(map);
\t\t{class_name_lower}Service.add{class_name_cap}({class_name_lower});
\t右

\t@RequestMapping(value = "api/{class_name_lower}/update{class_name_cap}")
\t@ResponseBody // 更新{class_name_cap}
\tpublic void update{class_name_cap}(@CookieValue("JSESSIONID") String JSESSIONID, @RequestBody Map<String, Object> map) 左
\t\t//User user = userService.getUserByJSESSIONID(JSESSIONID);
\t\t{class_name_cap} {class_name_lower} = new {class_name_cap}(map);
\t\t{class_name_lower}Service.update{class_name_cap}({class_name_lower});
\t右

\t@RequestMapping(value = "api/{class_name_lower}/delete{class_name_cap}")
\t@ResponseBody // 删除{class_name_cap}
\tpublic void delete{class_name_cap}(@CookieValue("JSESSIONID") String JSESSIONID, @RequestBody Map<String, Object> map) 左
\t\t//User user = userService.getUserByJSESSIONID(JSESSIONID);
\t\t{class_name_cap} {class_name_lower} = new {class_name_cap}(map);
\t\t{class_name_lower}Service.delete{class_name_cap}({class_name_lower});
\t右

\t@RequestMapping(value = "api/{class_name_lower}/get{class_name_cap}")
\t@ResponseBody // 获取{class_name_cap}
\tpublic String get{class_name_cap}(@CookieValue("JSESSIONID") String JSESSIONID, @RequestBody Map<String, Object> map) 左
\t\t//User user = userService.getUserByJSESSIONID(JSESSIONID);
\t\tString {class_name_lower}Id = map.get("{class_name_lower}Id").toString();
\t\t{class_name_cap} {class_name_lower} = {class_name_lower}Service.get{class_name_cap}ById({class_name_lower}Id);
\t\tMap frontResultMap = new HashMap();
\t\tMap data = toMap({class_name_lower});
\t\tfrontResultMap.put("data", data);
\t\treturn JSON.toJSONString(frontResultMap);
\t右
'''
    req_str = req_template.format(
        class_name_lower=table_name.lower(),
        class_name_cap=table_name_cap,
    )

    controller_str = controller_template.format(
        class_name_lower=table_name.lower(),
        class_name_cap=table_name_cap,
        package_path=package_path,
        tojson=tojson_str,
        req=req_str
    )
    controller_str = controller_str.replace('左', '{').replace('右', '}')

    with open(base_path + 'controller' + os.sep + '{}Controller.java'.format(table_name_cap), 'w',
              encoding='utf-8') as f:
        f.write(controller_str.replace('\n\n\n', '\n\n'))

    # Mapping
    print('提示：为{}构建Mapping'.format(table_name))
    for fk in fk_properties:
        dao_template += '''import {}.pojo.{};\n'''.format(package_path, fk.capitalize())

    mapping_template = '''<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE mapper
        PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
        "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="{package_path}.dao.{table_name_cap}DAO">

\t<!-- resultMap -->\t{resultMap}

\t<!-- add -->\t{add}

\t<!-- update -->\t{update}

\t<!-- delete -->\t{delete}

\t<!-- select -->\t{select}

</mapper>
'''
    resultMap_template = '''
\t<resultMap type="{package_path}.pojo.{table_name_cap}" id="{table_name_cap}ResultMap">
\t\t<id property="id" column="{class_name_lower}_id"/>{resultMapContent}
\t</resultMap>'''
    resultMapContent = ''
    for _name, _type in properties_name_type:
        if _name != 'id' and _name not in fk_properties:
            resultMapContent += '\n\t\t<result property="{class_name_lower}" column="{table_name}_{class_name_lower}" javaType="{class_type}"/>'.format(
                class_type=_type, table_name=table_name.lower(), class_name_lower=_name.lower())
    resultMapContent += '\n'
    for _name, _type in properties_name_type:
        if _name != 'id' and _name in fk_properties:
            resultMapContent += '\n\t\t<association property="{class_name_lower}" column="左{class_type_lower}Id={table_name}_{class_name_lower}右" select="{package_path}.dao.{class_type_cap}DAO.get{class_type_cap}ById" />'.format(
                class_type_lower=_type.lower(), class_name_lower=_name.lower(), table_name=table_name.lower(),
                class_type_cap=_type.capitalize(), package_path=package_path)
    resultMapContent = resultMapContent.replace('左', '{').replace('右', '}')

    resultMap_str = resultMap_template.format(
        package_path=package_path,
        table_name_cap=table_name_cap,
        class_name_lower=table_name.lower(),
        resultMapContent=resultMapContent
    )

    delete_template = '''
\t<delete id="delete{table_name_cap}" parameterType="{package_path}.pojo.{table_name_cap}">
\t\tdelete from {table_name_cap} where {class_name_lower}_id = #左{class_name_lower}.id右;
\t</delete>
\t<delete id="delete{table_name_cap}ById">
\t\tdelete from {table_name_cap} where {class_name_lower}_id = #左{class_name_lower}Id右;
\t</delete>
'''
    delete_str = delete_template.format(
        package_path=package_path,
        table_name_cap=table_name_cap,
        class_name_lower=table_name.lower()
    )
    delete_str = delete_str.replace('左', '{').replace('右', '}')

    select_template = '''
\t<select id="get{table_name_cap}" parameterType="{package_path}.pojo.{table_name_cap}" resultMap="{table_name_cap}ResultMap">
\t\tselect * from {table_name_cap} where {class_name_lower}_id = #左{class_name_lower}.id右;
\t</select>
\t<select id="get{table_name_cap}ById" resultMap="{table_name_cap}ResultMap">
\t\tselect * from {table_name_cap} where {class_name_lower}_id = #左{class_name_lower}Id右;
\t</select>
\t<select id="getAll{table_name_cap}s" resultMap="{table_name_cap}ResultMap">
\t\tselect * from {table_name_cap};
\t</select>'''
    select_str = select_template.format(
        package_path=package_path,
        table_name_cap=table_name_cap,
        class_name_lower=table_name.lower()
    )
    select_str = select_str.replace('左', '{').replace('右', '}')

    insert_template = '''
\t<insert id="add{table_name_cap}" parameterType="{package_path}.pojo.{table_name_cap}"
        useGeneratedKeys="true" keyProperty="{table_name_lower}.id">
\t\tinsert into {table_name_cap} ({key}
\t\t) value (\t\t\t{val}
\t\t);
\t</insert>'''

    key_list = []
    val_list = []
    for property_name, class_type in properties_name_type:
        if property_name == 'id':
            continue
        if class_type == 'String':
            key_list.append((
                '\n\t\t<if test=" {table_name}.{property_name} != null and {table_name}.{property_name} !='' ">\n\t\t\t, '.format(
                    table_name=table_name.lower(), property_name=property_name),
                '{table_name}_{property_name}'.format(table_name=table_name.lower(), property_name=property_name),
                '\n\t\t</if>'
            ))
            if property_name not in fk_properties:
                val_list.append((
                    '''\n\t\t<if test=" {table_name}.{property_name} != null and {table_name}.{property_name} !='' ">\n\t\t\t, '''.format(
                        table_name=table_name.lower(), property_name=property_name),
                    '''#左{table_name}.{property_name}右'''.format(table_name=table_name.lower(),
                                                                 property_name=property_name),
                    '''\n\t\t</if>
                    '''.format(table_name=table_name.lower(), property_name=property_name)
                ))
            else:
                val_list.append((
                    '''\n\t\t<if test=" {table_name}.{property_name} != null and {table_name}.{property_name} !='' ">\n\t\t\t, '''.format(
                        table_name=table_name.lower(), property_name=property_name),
                    '''#左{table_name}.{property_name}.id右'''.format(table_name=table_name.lower(),
                                                                    property_name=property_name),
                    '''\n\t\t</if>
                    '''.format(table_name=table_name.lower(), property_name=property_name)
                ))
        else:
            key_list.append((
                '\n\t\t<if test=" {table_name}.{property_name} != null ">\n\t\t\t, '.format(
                    table_name=table_name.lower(), property_name=property_name),
                '{table_name}_{property_name}'.format(table_name=table_name.lower(), property_name=property_name),
                '\n\t\t</if>'
            ))

            if property_name not in fk_properties:
                val_list.append((
                    '''\n\t\t<if test=" {table_name}.{property_name} != null ">\n\t\t\t, '''.format(
                        table_name=table_name.lower(), property_name=property_name),
                    '''#左{table_name}.{property_name}右'''.format(table_name=table_name.lower(),
                                                                 property_name=property_name),
                    '''\n\t\t</if>
                    '''.format(table_name=table_name.lower(), property_name=property_name)
                ))
            else:

                val_list.append((
                    '''\n\t\t<if test=" {table_name}.{property_name} != null ">\n\t\t\t, '''.format(
                        table_name=table_name.lower(), property_name=property_name),
                    '''#左{table_name}.{property_name}.id右'''.format(table_name=table_name.lower(),
                                                                    property_name=property_name),
                    '''\n\t\t</if>
                    '''.format(table_name=table_name.lower(), property_name=property_name)
                ))

    key = ''
    val = ''

    for idx, li in enumerate(key_list):
        if idx == 0:
            key += '\n\t\t' + li[1]
        else:
            key += ''.join(li)
    for idx, li in enumerate(val_list):
        if idx == 0:
            val += '\n\t\t' + li[1]
        else:
            val += ''.join(li)

    insert_str = insert_template.format(
        package_path=package_path,
        table_name_cap=table_name_cap,
        table_name_lower=table_name.lower(),
        key=key,
        val=val
    )
    insert_str = insert_str.replace('左', '{').replace('右', '}')

    update_template = '''
\t<update id="update{table_name_cap}" parameterType="{package_path}.pojo.{table_name_cap}" >
\t\tupdate {table_name_cap} set
\t\t{table_name_lower}_id = #左{table_name_lower}.id右
{set_str}
\t\twhere {table_name_lower}_id = #左{table_name_lower}.id右;
\t</update>'''
    set_str = ''
    for property_name, class_type in properties_name_type:
        if property_name == 'id':
            continue
        if class_type == 'String':
            if property_name not in fk_properties:
                set_str += '''\t\t<if test=" {table_name}.{property_name} != null and {table_name}.{property_name} !='' ">
\t\t\t, {table_name}_{property_name}=#左{table_name}.{property_name}右
\t\t</if>\n'''.format(table_name=table_name.lower(), property_name=property_name)
            else:
                set_str += '''\t\t<if test=" {table_name}.{property_name} != null and {table_name}.{property_name} !='' ">
\t\t\t, {table_name}_{property_name}=#左{table_name}.{property_name}.id右
\t\t</if>\n'''.format(table_name=table_name.lower(), property_name=property_name)

        else:
            if property_name not in fk_properties:
                set_str += '''\t\t<if test=" {table_name}.{property_name} != null ">
\t\t\t, {table_name}_{property_name}=#左{table_name}.{property_name}右
\t\t</if>\n'''.format(table_name=table_name.lower(), property_name=property_name)
            else:
                set_str += '''\t\t<if test=" {table_name}.{property_name} != null ">
\t\t\t, {table_name}_{property_name}=#左{table_name}.{property_name}.id右
\t\t</if>\n'''.format(table_name=table_name.lower(), property_name=property_name)

    set_str = set_str.replace('左', '{').replace('右', '}')
    update_str = update_template.format(
        package_path=package_path,
        table_name_cap=table_name_cap,
        table_name_lower=table_name.lower(),
        set_str=set_str
    )
    update_str = update_str.replace('左', '{').replace('右', '}')

    other_str = ''
    # 单个外键查删
    for fk_property in fk_properties:
        other_str += '''
\t<select id="get{table_name_cap}By{fk_property_cap}" parameterType="{package_path}.pojo.{fk_property_cap}" resultMap="{table_name_cap}ResultMap">
\t\tselect * from {table_name_cap} where {fk_property_lower}_id = #左{fk_property_lower}.id右;
\t</select>
\t<select id="get{table_name_cap}sBy{fk_property_cap}" parameterType="{package_path}.pojo.{fk_property_cap}" resultMap="{table_name_cap}ResultMap">
\t\tselect * from {table_name_cap} where {fk_property_lower}_id = #左{fk_property_lower}.id右;
\t</select>

\t<delete id="get{table_name_cap}By{fk_property_cap}" parameterType="{package_path}.pojo.{fk_property_cap}" resultMap="{table_name_cap}ResultMap">
\t\tdelete * from {table_name_cap} where {fk_property_lower}_id = #左{fk_property_lower}.id右;
\t</delete>
\t<delete id="get{table_name_cap}sBy{fk_property_cap}" parameterType="{package_path}.pojo.{fk_property_cap}" resultMap="{table_name_cap}ResultMap">
\t\tdelete * from {table_name_cap} where {fk_property_lower}_id = #左{fk_property_lower}.id右;
\t</delete>
'''.format(
        package_path=package_path,
        table_name_cap=table_name_cap,
        fk_property_cap=fk_property.capitalize(),
        fk_property_lower=fk_property.lower()
    )

    # 联合外键查删
    other_str += ''''
\t<select id="get{table_name_cap}By{fk_properties}" resultMap="{table_name_cap}ResultMap">
\t\tselect * from {table_name_cap} where {fk_properties_condition};
\t</select>
\t<select id="get{table_name_cap}sBy{fk_properties}" resultMap="{table_name_cap}ResultMap">
\t\tselect * from {table_name_cap} where {fk_properties_condition};
\t</select>

\t<delete id="delete{table_name_cap}By{fk_properties}" resultMap="{table_name_cap}ResultMap">
\t\tdelete * from {table_name_cap} where {fk_properties_condition};
\t</delete>
\t<delete id="delete{table_name_cap}sBy{fk_properties}" resultMap="{table_name_cap}ResultMap">
\t\tdelete * from {table_name_cap} where {fk_properties_condition};
\t</delete>
'''.format(fk_properties='And'.join([fk_property.capitalize()+'Id' for fk_property in fk_properties]),
           fk_properties_condition=' and '.join(['{fk_property_lower}_id = #左{fk_property_lower}Id右'.format(fk_property_lower=fk_property.lower())
                                          for fk_property in fk_properties]),
           table_name_cap=table_name_cap)
    other_str = other_str.replace('左', '{').replace('右', '}')

    mapping_str = mapping_template.format(
        package_path=package_path,
        table_name_cap=table_name_cap,
        table_name=table_name.lower(),
        resultMap=resultMap_str,
        add=insert_str,
        delete=delete_str,
        update=update_str,
        select=select_str,
        other_str=other_str

    )
    with open(base_path + 'mapping' + os.sep + '{}Mapper.xml'.format(table_name_cap), 'w',
              encoding='utf-8') as f:
        f.write(mapping_str)
        # input()
# 添加 UserExample 表
print('\n提示: 添加 userexample 表\n')
sql = 'use ' + db_name + ';'
cursor.execute(sql)
sql = '''CREATE TABLE `userexample` (
  `userExample_id`         INT(6) AUTO_INCREMENT NOT NULL,
  `userExample_openid`     CHAR(28)    DEFAULT NULL,
  `userExample_sessionid`  CHAR(32)    DEFAULT NULL,
  `userExample_sessionkey` TEXT        DEFAULT NULL,
  `userExample_avatarUrl`  TEXT        DEFAULT NULL,
  PRIMARY KEY (`userExample_id`),
  UNIQUE (`userExample_openid`),
  UNIQUE (`userExample_sessionid`)
)
  ENGINE = InnoDB
  DEFAULT CHARSET = utf8;
'''
cursor.execute(sql)
db.commit()

# 关闭数据库连接
db.close()

print('功能：根据 MySQL 数据库生成SSM代码')
print('提示：请手动添加 tomcat-api.jar servlet-api.jar，jar包位于apache-tomcat目录下的lib目录')
print('提示：请处理好Maven中jar包')
print('webapp目录：{db_name_cap}{sep}src{sep}src{sep}main{sep}webapp'.format(sep=sep, db_name_cap=db_name_cap))
print('\n针对小程序：')
print('\n\t在UserExampleController中的login方法填写好Appid及SecretId')
print('\n\t用户表应有字段保存sessionid, 在LoginInterceptor中过滤非法sessionid, 在Controller中根据sessionid获取用户实例')
print('\n\t在 web.xml 中填写 appid 及 secret')


