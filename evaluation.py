def evaluate(pred, gt):

    # --- gestione errori ---
    if isinstance(pred, dict) or isinstance(gt, dict):
        return {
            "cell_precision": 0,
            "cell_recall": 0,
            "tuple_cardinality": 0,
            "tuple_constraint": 0,
            "tuple_order": 0
        }

    # --- flatten celle ---
    pred_cells = [cell for row in pred for cell in row]
    gt_cells = [cell for row in gt for cell in row]

    # --- cell precision ---
    correct_cells = sum(1 for c in pred_cells if c in gt_cells)

    cell_precision = correct_cells / len(pred_cells) if pred_cells else 0
    cell_recall = correct_cells / len(gt_cells) if gt_cells else 0

    # --- tuple cardinality ---
    tuple_cardinality = len(pred) / len(gt) if gt else 0

    # --- tuple constraint (set match) ---
    pred_set = set(pred)
    gt_set = set(gt)

    correct_tuples = len(pred_set & gt_set)

    tuple_constraint = correct_tuples / len(gt_set) if gt_set else 0

    # --- tuple order ---
    correct_order = sum(1 for p, g in zip(pred, gt) if p == g)

    tuple_order = correct_order / len(gt) if gt else 0

    return {
        "cell_precision": cell_precision,
        "cell_recall": cell_recall,
        "tuple_cardinality": tuple_cardinality,
        "tuple_constraint": tuple_constraint,
        "tuple_order": tuple_order
    }