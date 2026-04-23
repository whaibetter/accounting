package com.accounting.app.api

import retrofit2.http.*

interface ApiService {

    @POST("auth/login")
    suspend fun login(@Body request: LoginRequest): ApiResponse<LoginResponse>

    @GET("accounts")
    suspend fun listAccounts(): ApiResponse<List<Account>>

    @POST("accounts")
    suspend fun createAccount(@Body account: AccountCreate): ApiResponse<Account>

    @DELETE("accounts/{id}")
    suspend fun deleteAccount(@Path("id") id: Int): ApiResponse<Any?>

    @GET("categories")
    suspend fun listCategories(@Query("type") type: Int? = null): ApiResponse<List<Category>>

    @GET("tags")
    suspend fun listTags(): ApiResponse<List<Tag>>

    @POST("tags")
    suspend fun createTag(@Body tag: TagCreate): ApiResponse<Tag>

    @DELETE("tags/{id}")
    suspend fun deleteTag(@Path("id") id: Int): ApiResponse<Any?>

    @GET("bills")
    suspend fun listBills(
        @Query("page") page: Int = 1,
        @Query("size") size: Int = 20,
        @Query("start_date") startDate: String? = null,
        @Query("end_date") endDate: String? = null,
        @Query("type") type: Int? = null,
        @Query("category_id") categoryId: Int? = null,
        @Query("account_id") accountId: Int? = null,
        @Query("keyword") keyword: String? = null
    ): ApiResponse<PagedData<Bill>>

    @POST("bills")
    suspend fun createBill(@Body bill: BillCreate): ApiResponse<Bill>

    @PUT("bills/{id}")
    suspend fun updateBill(@Path("id") id: Int, @Body bill: BillUpdate): ApiResponse<Bill>

    @DELETE("bills/{id}")
    suspend fun deleteBill(@Path("id") id: Int): ApiResponse<Any?>

    @GET("statistics/overview")
    suspend fun getOverview(
        @Query("start_date") startDate: String? = null,
        @Query("end_date") endDate: String? = null
    ): ApiResponse<Overview>

    @GET("statistics/by-category")
    suspend fun getCategoryStats(
        @Query("start_date") startDate: String? = null,
        @Query("end_date") endDate: String? = null,
        @Query("type") type: Int = 1
    ): ApiResponse<List<CategoryStat>>

    @GET("statistics/trend")
    suspend fun getTrend(
        @Query("start_date") startDate: String,
        @Query("end_date") endDate: String,
        @Query("granularity") granularity: String = "day"
    ): ApiResponse<List<TrendItem>>

    @POST("import/accounts")
    suspend fun importAccounts(@Body accounts: Map<String, List<Map<String, @JvmSuppressWildcards Any>>>): ApiResponse<ImportResult>

    @POST("import/bills")
    suspend fun importBills(@Body bills: Map<String, List<Map<String, @JvmSuppressWildcards Any>>>): ApiResponse<ImportResult>
}
