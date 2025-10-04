SELECT 
    "employee_financemanagerkpi"."id",
    "employee_financemanagerkpi"."filial_id",
    "employee_financemanagerkpi"."is_archived",
    "employee_financemanagerkpi"."archived_at",
    "employee_financemanagerkpi"."created_at", 
    "employee_financemanagerkpi"."updated_at", 
    "employee_financemanagerkpi"."deleted_at", 
    "employee_financemanagerkpi"."create_context", 
    "employee_financemanagerkpi"."update_context", 
    "employee_financemanagerkpi"."employee_id", 
    "employee_financemanagerkpi"."action", 
    "employee_financemanagerkpi"."range", 
    "employee_financemanagerkpi"."amount" 
FROM "employee_financemanagerkpi" 
WHERE (
            "employee_financemanagerkpi"."employee_id" = b18ef020-7a11-49d9-8ef3-a71ca7d723d6 
        AND 
            "employee_financemanagerkpi"."range" @> (50)::numeric(None, 
    None)) ORDER BY "employee_financemanagerkpi"."created_at" DESC'