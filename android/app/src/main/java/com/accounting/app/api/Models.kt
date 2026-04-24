package com.accounting.app.api

import com.google.gson.annotations.SerializedName

data class ApiResponse<T>(
    val code: Int = 200,
    val message: String = "success",
    val data: T? = null
)

data class LoginRequest(val password: String)

data class LoginResponse(val access_token: String)

data class Account(
    val id: Int,
    val name: String,
    val type: Int,
    val icon: String = "",
    val color: String = "",
    val balance: Double = 0.0,
    val initial_balance: Double = 0.0,
    val is_default: Int = 0,
    val status: Int = 1,
    val created_at: String = "",
    val updated_at: String = ""
)

data class AccountCreate(
    val name: String,
    val type: Int,
    val icon: String = "",
    val color: String = "",
    val initial_balance: Double = 0.0,
    val is_default: Boolean = false
)

data class Category(
    val id: Int,
    val parent_id: Int? = null,
    val name: String,
    val type: Int,
    val icon: String = "",
    val sort_order: Int = 0,
    val children: List<Category> = emptyList()
)

data class Tag(
    val id: Int,
    val name: String,
    val color: String = "",
    val created_at: String = ""
)

data class TagCreate(
    val name: String,
    val color: String = ""
)

data class Bill(
    val id: Int,
    val account_id: Int,
    val account_name: String = "",
    val category_id: Int,
    val category_name: String = "",
    val category_icon: String = "",
    val type: Int,
    val amount: Double,
    val bill_date: String,
    val bill_time: String? = null,
    val remark: String = "",
    val tags: List<TagBrief> = emptyList(),
    val transfer_to_account_id: Int? = null,
    val created_at: String = "",
    val updated_at: String = ""
)

data class TagBrief(
    val id: Int,
    val name: String,
    val color: String = ""
)

data class BillCreate(
    val account_id: Int,
    val category_id: Int,
    val type: Int,
    val amount: Double,
    val bill_date: String,
    val bill_time: String? = null,
    val remark: String = "",
    val tag_ids: List<Int> = emptyList(),
    val transfer_to_account_id: Int? = null
)

data class BillUpdate(
    val account_id: Int? = null,
    val category_id: Int? = null,
    val type: Int? = null,
    val amount: Double? = null,
    val bill_date: String? = null,
    val bill_time: String? = null,
    val remark: String? = null,
    val tag_ids: List<Int>? = null,
    val transfer_to_account_id: Int? = null
)

data class PagedData<T>(
    val items: List<T>,
    val total: Int,
    val page: Int,
    val size: Int
)

data class Overview(
    val total_income: Double = 0.0,
    val total_expense: Double = 0.0,
    val balance: Double = 0.0,
    val bill_count: Int = 0
)

data class CategoryStat(
    val category_id: Int,
    val category_name: String,
    val category_icon: String = "",
    val amount: Double = 0.0,
    val percentage: Double = 0.0,
    val bill_count: Int = 0
)

data class TrendItem(
    val period: String,
    val income: Double = 0.0,
    val expense: Double = 0.0
)

data class ImportResult(
    val success: Int = 0,
    val skipped: Int? = null,
    val errors: List<Any> = emptyList()
)

data class LlmConfigResponse(
    val api_key: String? = null,
    val api_base: String? = null,
    val model: String? = null,
    val provider: String? = null,
    val temperature: Double? = null,
    val max_tokens: Int? = null
)
