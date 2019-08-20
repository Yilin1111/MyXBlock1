import pandas as pd
from string import Template

# 文件读取
file_path = 'C:/Users/z50008114/Desktop/Hi1280V100 LocalBus 寄存器描述.xlsm'
template_path = 'C:/Users/z50008114/Desktop/kdc_dfx_v8_template.c'
product_path = 'C:/Users/z50008114/Desktop/kdc_dfx_v8_'
register_info = pd.read_excel(file_path, sheet_name='LocalBus', usecols=[0, 3, 4, 7, 9, 10, 11, 12, 13],
                              skip_blank_lines=True)
register_info.columns = ['register_name', 'offset', 'width', 'register_initial', 'member_name', 'member_range',
                         'attribute', 'member_initial', 'constraint']               # 修改列名称

# 变量赋值
start_row = 5
end_row = register_info.shape[0]
register_name = register_info['register_name']
offset = register_info['offset']
width = register_info['width']
register_initial = register_info['register_initial']
member_name = register_info['member_name']
member_range = register_info['member_range']
attribute = register_info['attribute']
member_initial = register_info['member_initial']
g_port_base_context = ''
g_port_reg_context = ''
module_name = 'lbc'
parent_module_name = 'lbc_parent'
template_file = open(template_path, encoding='UTF-8')
product_file = open(product_path + module_name + '.c', 'w')

# 获得g_port_base_context和g_port_reg
for i in range(start_row, end_row):
    if str(register_name.loc[i]) == 'nan':
        continue
    g_port_base_context += '\n\t{"' + str(register_name.loc[i]) + '", ' + str(register_initial.loc[i]) + ', ' + str(
        offset.loc[i]) + '},'
    g_port_reg_context += '\n\t{"' + str(register_name.loc[i]) + '", ' + str(offset.loc[i]) + '},'

# 生成代码
lines = []
temp = Template(template_file.read())
lines.append(temp.substitute(
    g_port_base_context=g_port_base_context, g_port_reg_context=g_port_reg_context,
    module_name=module_name, parent_module_name=parent_module_name))
product_file.writelines(lines)
template_file.close()
product_file.close()
print('File "kdc_dfx_v8_' + module_name + '.c" has created!')
