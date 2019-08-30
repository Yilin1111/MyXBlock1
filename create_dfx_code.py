import sys
import time
import xlrd
import pandas as pd
from string import Template

# 文件读取
file_path = 'C:/Users/z50008114/Desktop/kdc_tables/Hi1280V100 HHA 寄存器描述.xlsm'
template_path = 'C:/Users/z50008114/Desktop/kdc_code/kdc_dfx_v8_template.c'
product_path = 'C:/Users/z50008114/Desktop/kdc_code/kdc_dfx_v8_'
task_file_path = 'C:/Users/z50008114/Desktop/kdc_tables/module_detail.xlsx'
module_sheet_list = xlrd.open_workbook(file_path).sheet_names()
print('Start reading detail file...')
task_info = pd.read_excel(task_file_path, sheet_name='detail', skip_blank_lines=True)
template_file = open(template_path, encoding='UTF-8')

# 需求文件有效性检查
module_list = task_info['module_name']
sheet_list = task_info['sheet_name']
parent_list = task_info['parent_dic']
start_offset_list = task_info['start_offset']
end_offset_list = task_info['end_offset']
for i in range(len(module_list)):
    if sheet_list[i] not in module_sheet_list:
        print('Sheet "' + sheet_list[i] + '" does not exist!')
        sys.exit(-1)
    if int(start_offset_list[i], 16) > int(end_offset_list[i], 16):
        print('In line ' + str(i+1) + ' start offset must not be larger than end offset!')
        sys.exit(-1)

# 读取偏移量中的变量范围(这里是单模块，之后要改为多模块、读取模块名)
var_info = pd.read_excel(file_path, sheet_name='reg_var', skip_blank_lines=True, skiprows=4, usecols=[0, 1])
var_name_list = var_info['Name']
var_range_list = var_info['Range']
var_start_range_list = []
var_end_range_list = []
for var_range in var_range_list:
    var_start_range_list.append(var_range.split('~')[0])
    var_end_range_list.append(var_range.split('~')[1])

# 按模块生成代码
module_names = list(set(module_list))                                       # module_names是去重排序后的模块名列表
for module_name in module_names:                                            # 每个模块遍历
    print('Start creating module "' + module_name + '"...')
    # 初始化模块公用变量
    g_port_base_context = ''
    g_port_reg_context = ''
    parent_dic = ''
    product_file = open(product_path + module_name + '.c', 'w')

    # 获取当前模块的父文件夹
    for data_id in range(len(module_list)):
        if module_name == module_list[data_id]:
            parent_dic = parent_list[data_id]
            break
    sheet_names = []                                                        # 当前模块包含的工作表名去重列表
    for data_id in range(len(module_list)):                                 # 每条数据遍历
        if (module_name == module_list[data_id]) and (sheet_list[data_id] not in sheet_names):
            sheet_names.append(sheet_list[data_id])

    # 读取表单数据
    for sheet_name in sheet_names:                                          # 每个工作表遍历
        register_info = pd.read_excel(file_path, sheet_name=sheet_name, usecols=[0, 1, 3], skip_blank_lines=True,
                                      header=None)
        # 修改列名称
        register_info.columns = ['register_name', 'description', 'offset']

        # 表单内变量赋值
        start_row = 6
        end_row = register_info.shape[0]
        initial_register_name = register_info['register_name']              # 初始寄存器名列表（含+偏移的寄存器未拆分，大小为初始大小）
        description = register_info['description']                          # 寄存器描述列表，主要用于获得模块名、基地址等
        initial_offset = register_info['offset']                            # 初始偏移列表（含+字符，大小为初始大小）
        largest_offset = 0                                                  # 最大偏移量（一个数值）
        largest_register_name_size = 0                                      # 寄存器名最大长度（一个数值）
        register_name_size = []                                             # 最终寄存器名size大小（便于对齐，大小为最终大小）
        need_print = []                                                     # 寄存器名是否需要打印（大小为最终大小）
        start_offsets = []                                                  # 打印出的偏移范围开始值列表（大小为需求文件数据条数）
        end_offsets = []                                                    # 打印出的偏移范围结束值列表（大小为需求文件数据条数）
        offsets = []                                                        # 最终偏移列表（大小为最终大小）
        register_names = []                                                 # 最终寄存器名列表（含+偏移的寄存器未拆分，大小为最终大小）

        # 获取当前工作表的偏移范围
        print('Base "' + str(description[0]) + '" has been created!')
        for data_id in range(len(module_list)):                             # 每条数据遍历
            if (module_name == module_list[data_id]) and (sheet_list[data_id] == sheet_name):
                start_offsets.append(int(start_offset_list[data_id], 16))
                end_offsets.append(int(end_offset_list[data_id], 16))

        # 获取模块最大偏移和最长寄存器名（便于对齐）
        for i in range(start_row, end_row):                                 # 每条初始数据遍历
            if str(initial_register_name[i]) == 'nan' or str(initial_offset[i]) == 'nan':
                continue
            offset_list = str(initial_offset[i]).replace(' ', '').replace('\n', '').split('+')
            curr_offset = 0                                                 # 当前偏移量
            var_start_offset = 0                                            # 变量偏移变量开始范围
            var_end_offset = 0                                              # 变量偏移变量结束范围
            var_unit = 0                                                    # 变量偏移单位数值
            need_print_flag = 0                                             # 当前寄存器是否需要打印（偏移地址在打印范围内）
            for j in range(len(offset_list)):                               # 遍历数据偏移字符串拆分后的列表
                # 无变量部分累加
                if offset_list[j].isalnum():
                    curr_offset += int(offset_list[j], 16)
                # 有变量部分取最大值
                else:
                    var_part_list = offset_list[j].split('*')
                    for k in range(len(var_part_list)):                     # 遍历数据偏移字符串拆分后的列表元素中有+部分的元素（按*）拆分
                        # 数值部分
                        if var_part_list[k].find('0x') >= 0 or var_part_list[k].find('0X') >= 0:
                            var_unit = int(var_part_list[k], 16)
                        # 变量名部分
                        else:
                            for var_id in range(len(var_name_list)):        # 遍历变量名列表寻找匹配变量
                                if var_part_list[k] == var_name_list[var_id]:
                                    var_start_offset = int(var_start_range_list[var_id])
                                    var_end_offset = int(var_end_range_list[var_id]) + 1
                                    break

            # 为无+的寄存器添加终版列表
            if len(offset_list) == 1:
                register_names.append(initial_register_name[i])
                register_name_size.append(len(register_names[-1]))
                offsets.append(curr_offset)
                for j in range(len(start_offsets)):                         # 遍历寄存器打印范围起止范围判断是否需要打印
                    if (curr_offset >= start_offsets[j]) and (curr_offset <= end_offsets[j]):
                        need_print_flag = 1
                        break
                if need_print_flag:
                    need_print.append(1)
                else:
                    need_print.append(0)

            # 为有+的寄存器添加终版列表
            else:
                for j in range(len(start_offsets)):                         # 遍历寄存器打印范围起止范围判断是否需要打印
                    if (curr_offset >= start_offsets[j]) and (curr_offset <= end_offsets[j]):
                        need_print_flag = 1
                        break
                for sub_id in range(var_start_offset, var_end_offset):
                    register_names.append(initial_register_name[i].replace(' ', '') + '_' + str(sub_id))
                    register_name_size.append(len(register_names[-1]))
                    offsets.append(curr_offset + sub_id * var_unit)
                    if need_print_flag:
                        need_print.append(1)
                    else:
                        need_print.append(0)

            # 获取最大偏移和最大寄存器名字长度
            largest_offset = max(offsets)
            largest_register_name_size = max(register_name_size)

        # 获得g_port_base_context和g_port_reg
        g_port_base_context += '\n    {"' + str(description[0]) + '", ' + str(description[2]).replace('_', '') + \
                               ', ' + str(hex(int(largest_offset/4096)*4096+4096)) + '},'
        for i in range(len(register_names)):
            if need_print[i] == 0:
                continue
            space_num = largest_register_name_size - register_name_size[i]
            space_context = ''
            for j in range(0, space_num):
                space_context += ' '
            g_port_reg_context += '\n    {"' + register_names[i] + '", ' + space_context + str(hex(offsets[i])) + '},'

    # 按模块生成代码
    lines = []
    temp = Template(template_file.read())
    lines.append(temp.substitute(
        g_port_base_context=g_port_base_context, g_port_reg_context=g_port_reg_context, module_name=module_name,
        parent_module_name=parent_dic, create_date=time.strftime('%Y/%m/%d', time.localtime(time.time()))))
    product_file.writelines(lines)
    template_file.close()
    product_file.close()
    print('File "kdc_dfx_v8_' + module_name + '.c" has been created!')

print('All code files have been created!')
