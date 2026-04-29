from collections import Counter

def evaluate(pred, gt):

    # -----------------------
    # NORMALIZZAZIONE INPUT
    # -----------------------
    pred_llama = []
    pred_gpt = []
    gt_pred = []

    for item in pred:
        pred_llama.extend(item.get("llama", []))
        pred_gpt.extend(item.get("gpt", []))

    for item in gt:
        gt_pred.extend(item.get("prediction", []))

    # converti in tuple
    pred_llama = [tuple(row) for row in pred_llama]
    pred_gpt = [tuple(row) for row in pred_gpt]
    gt_pred = [tuple(row) for row in gt_pred]

    # -----------------------
    # 1. CELL METRICS
    # -----------------------

    pred_llama_cells = [c for row in pred_llama for c in row]
    pred_gpt_cells = [c for row in pred_gpt for c in row]
    gt_cells = [c for row in gt_pred for c in row]

    # total predicted cells
    pred_llama_counter = Counter(pred_llama_cells)
    pred_gpt_counter = Counter(pred_gpt_cells)
    # total ground truth cells
    gt_counter = Counter(gt_cells)

    # total correct cells
    correct_llama_cells = sum((pred_llama_counter & gt_counter).values())
    correct_gpt_cells = sum((pred_gpt_counter & gt_counter).values())

    # precision = correct / total predicted
    cell_llama_precision = correct_llama_cells / len(pred_llama_cells) if pred_llama_cells else 0
    cell_gpt_precision = correct_gpt_cells / len(pred_gpt_cells) if pred_gpt_cells else 0

    # recall = correct / total ground truth
    cell_llama_recall = correct_llama_cells / len(gt_cells) if gt_cells else 0
    cell_gpt_recall = correct_gpt_cells / len(gt_cells) if gt_cells else 0


    # -----------------------
    # 2. TUPLE METRICS
    # -----------------------

    pred_llama_set = set(pred_llama)
    pred_gpt_set = set(pred_gpt)
    gt_set = set(gt_pred)

    correct_llama_tuples = len(pred_llama_set & gt_set)
    correct_gpt_tuples = len(pred_gpt_set & gt_set)

    tuple_llama_constraint = correct_llama_tuples / len(pred_llama) if pred_llama else 0
    tuple_gpt_constraint = correct_gpt_tuples / len(pred_gpt) if pred_gpt else 0

    tuple_llama_cardinality = len(pred_llama) / len(gt_pred) if gt_pred else 0
    tuple_gpt_cardinality = len(pred_gpt) / len(gt_pred) if gt_pred else 0


    # -----------------------
    # 3. ORDER METRIC
    # -----------------------

    tuple_llama_order = sum(
        1 for i in range(min(len(pred_llama), len(gt_pred)))
        if pred_llama[i] == gt_pred[i]
    ) / len(gt_pred) if gt_pred else 0

    tuple_gpt_order = sum(
        1 for i in range(min(len(pred_gpt), len(gt_pred)))
        if pred_gpt[i] == gt_pred[i]
    ) / len(gt_pred) if gt_pred else 0


    # -----------------------
    # RESULT
    # -----------------------

    return {
        "llama": {
            "cell_precision": cell_llama_precision,
            "cell_recall": cell_llama_recall,
            "tuple_cardinality": tuple_llama_cardinality,
            "tuple_constraint": tuple_llama_constraint,
            "tuple_order": tuple_llama_order
        },
        "gpt": {
            "cell_precision": cell_gpt_precision,
            "cell_recall": cell_gpt_recall,
            "tuple_cardinality": tuple_gpt_cardinality,
            "tuple_constraint": tuple_gpt_constraint,
            "tuple_order": tuple_gpt_order
        }
    }