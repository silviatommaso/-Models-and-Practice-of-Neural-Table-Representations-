def remove_attributes(data):

    new_data = []

    for item in data:

        new_item = {
            "nl": item.get("nl"),
            "sql_llama": item.get("sql_llama"),
            "sql_gpt": item.get("sql_gpt")
        }

        # LLAMA
        llama_rows = item.get("llama", [])

        if isinstance(llama_rows, list):
            new_item["llama"] = [
                list(row.values()) for row in llama_rows
            ]
        else:
            new_item["llama"] = llama_rows

        # GPT
        gpt_rows = item.get("gpt", [])

        if isinstance(gpt_rows, list):
            new_item["gpt"] = [
                list(row.values()) for row in gpt_rows
            ]
        else:
            new_item["gpt"] = gpt_rows

        new_data.append(new_item)

    return new_data


def remove_attributes_ground_truth(data):

    new_data = []

    for item in data:

        new_item = {
            "nl": item.get("nl"),
            "sql": item.get("sql"),
            "prediction": item.get("prediction")
        }

        # LLAMA
        prediction = item.get("prediction", [])

        if isinstance(prediction, list):
            new_item["prediction"] = [
                list(row.values()) for row in prediction
            ]
        else:
            new_item["prediction"] = prediction


        new_data.append(new_item)

    return new_data