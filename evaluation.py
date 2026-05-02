from collections import Counter

def has_order_by(sql):
    return sql is not None and "ORDER BY" in sql.upper()


def evaluate(pred, gt):

    results = []

    for p_item, g_item in zip(pred, gt):

        # Normalizzazione: None -> []
        pred_llama = [tuple(row) for row in (p_item.get("llama") or [])]
        pred_gpt = [tuple(row) for row in (p_item.get("gpt") or [])]
        gt_pred = [tuple(row) for row in (g_item.get("prediction") or [])]

        gt_sql = g_item.get("sql", None)
        order_flag = has_order_by(gt_sql)

        # -----------------------
        # EMPTY CASE CHECK
        # -----------------------

        llama_empty_correct = (pred_llama == [] and gt_pred == [])
        gpt_empty_correct = (pred_gpt == [] and gt_pred == [])

        # -----------------------
        # 1. CELL METRICS
        # -----------------------

        pred_llama_cells = [c for row in pred_llama for c in row]
        pred_gpt_cells = [c for row in pred_gpt for c in row]
        gt_cells = [c for row in gt_pred for c in row]

        pred_llama_counter = Counter(pred_llama_cells)
        pred_gpt_counter = Counter(pred_gpt_cells)
        gt_counter = Counter(gt_cells)

        correct_llama_cells = sum((pred_llama_counter & gt_counter).values())
        correct_gpt_cells = sum((pred_gpt_counter & gt_counter).values())

        if llama_empty_correct:
            cell_llama_precision = 1
            cell_llama_recall = 1
        else:
            cell_llama_precision = correct_llama_cells / len(pred_llama_cells) if pred_llama_cells else 0
            cell_llama_recall = correct_llama_cells / len(gt_cells) if gt_cells else 0

        if gpt_empty_correct:
            cell_gpt_precision = 1
            cell_gpt_recall = 1
        else:
            cell_gpt_precision = correct_gpt_cells / len(pred_gpt_cells) if pred_gpt_cells else 0
            cell_gpt_recall = correct_gpt_cells / len(gt_cells) if gt_cells else 0

        # -----------------------
        # 2. TUPLE METRICS
        # -----------------------

        pred_llama_set = set(pred_llama)
        pred_gpt_set = set(pred_gpt)
        gt_set = set(gt_pred)

        correct_llama_tuples = len(pred_llama_set & gt_set)
        correct_gpt_tuples = len(pred_gpt_set & gt_set)

        if llama_empty_correct:
            tuple_llama_constraint = 1
            tuple_llama_cardinality = 1
        else:
            tuple_llama_constraint = correct_llama_tuples / len(pred_llama) if pred_llama else 0
            tuple_llama_cardinality = (
                min(len(pred_llama), len(gt_pred)) / max(len(pred_llama), len(gt_pred))
            ) if (pred_llama or gt_pred) else 0

        if gpt_empty_correct:
            tuple_gpt_constraint = 1
            tuple_gpt_cardinality = 1
        else:
            tuple_gpt_constraint = correct_gpt_tuples / len(pred_gpt) if pred_gpt else 0
            tuple_gpt_cardinality = (
                min(len(pred_gpt), len(gt_pred)) / max(len(pred_gpt), len(gt_pred))
            ) if (pred_gpt or gt_pred) else 0

        # -----------------------
        # 3. ORDER METRIC
        # -----------------------

        den = len(gt_pred)

        if order_flag and den == 0:
            tuple_llama_order = 1 if llama_empty_correct else 0
            tuple_gpt_order = 1 if gpt_empty_correct else 0
        else:
            tuple_llama_order = (
                sum(
                    1 for i in range(den)
                    if i < len(pred_llama) and pred_llama[i] == gt_pred[i]
                ) / den
            ) if (den > 0 and order_flag) else None

            tuple_gpt_order = (
                sum(
                    1 for i in range(den)
                    if i < len(pred_gpt) and pred_gpt[i] == gt_pred[i]
                ) / den
            ) if (den > 0 and order_flag) else None

        # -----------------------
        # 4. QUERY SCORE
        # -----------------------

        llama_components = [
            cell_llama_precision,
            cell_llama_recall,
            tuple_llama_cardinality,
            tuple_llama_constraint
        ]

        gpt_components = [
            cell_gpt_precision,
            cell_gpt_recall,
            tuple_gpt_cardinality,
            tuple_gpt_constraint
        ]

        if order_flag:
            llama_components.append(tuple_llama_order or 0)
            gpt_components.append(tuple_gpt_order or 0)

        llama_query_score = sum(llama_components) / len(llama_components) if llama_components else 0
        gpt_query_score = sum(gpt_components) / len(gpt_components) if gpt_components else 0

        # -----------------------
        # STORE RESULT
        # -----------------------

        results.append({
            "nl": g_item.get("nl"),
            "sql": gt_sql,

            "llama": {
                "cell_precision": cell_llama_precision,
                "cell_recall": cell_llama_recall,
                "tuple_cardinality": tuple_llama_cardinality,
                "tuple_constraint": tuple_llama_constraint,
                "tuple_order": tuple_llama_order,
                "query_score": llama_query_score
            },

            "gpt": {
                "cell_precision": cell_gpt_precision,
                "cell_recall": cell_gpt_recall,
                "tuple_cardinality": tuple_gpt_cardinality,
                "tuple_constraint": tuple_gpt_constraint,
                "tuple_order": tuple_gpt_order,
                "query_score": gpt_query_score
            }
        })

    return results