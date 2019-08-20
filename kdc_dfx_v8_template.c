/*
 * Copyright (c) Huawei Technologies Co., Ltd. 2012-2018. All rights reserved.
 * Description:
 * Author: hw 
 * Create: 2012/10/20
 */
#include <asm/page.h>
#include <linux/io.h>
#include <linux/slab.h>
#include <linux/platform_device.h>
#include <linux/of.h>
#include <linux/of_fdt.h>
#include "Drv_Log_K.h"
#include "Drv_Error_K.h"
#include "kdc_dfx.h"
#include "cpu_dfx_v8_adapter.h"
#include "kdc_dfx_common.h"
#include "kdc_cpu_dfx_api.h"

static u32 g_use_djtag_mode = 0;

static BASE_ITEM g_port_base[] = {${g_port_base_context}
};

static OFFSET_ITEM g_port_reg[] = {${g_port_reg_context}
};

static SHOW_REG_CTRL g_show = {
	{NULL, 0},
	{NULL, 0},
	{g_port_base, ARRAY_SIZE(g_port_base)},
	{g_port_reg, ARRAY_SIZE(g_port_reg)},
};

static const struct dfx_operations g_${module_name}_v8_dfx = {
	.show_brief = ${module_name}_show_brief,
	.show_detail = ${module_name}_show_detail,
	.show_error = ${module_name}_show_error,
	.show_his_error = ${module_name}_show_his_error,
	.show_stat = ${module_name}_show_stat,
	.show_register = ${module_name}_show_register,
	.show_loopback = NULL,
	.show_debug = ${module_name}_show_debug,
	.set_debug = ${module_name}_set_debug,
	.set_loopback = NULL,
};

static struct v8_dfx_reg_info g_v8_dfx_${module_name}_reg_info[] = {
	{
		.name = "${parent_module_name}",
		.parent = NULL,
		.dfx_ops = NULL,
	},
	{
		.name = "${module_name}",
		.parent = "${parent_module_name}",
		.dfx_ops = &g_${module_name}_v8_dfx,
	}
};

static V8_DFX_PRE_FUNC g_dfx_pre_func = NULL;

V8_DFX_TEMPLATE(${module_name})