from flask import Flask, render_template_string, request, jsonify
import pandas as pd

app = Flask(__name__)

# Set the fixed file path for your Excel file
file_path = "/Users/sri/Downloads/RENDER/PaReport-2.xlsx"

# Load the Excel file
original_data = pd.read_excel(file_path, sheet_name="Summary")

# Ensure QUANTITY and COST are numeric, filling NaN with 0
original_data["QUANTITY"] = pd.to_numeric(original_data["QUANTITY"], errors="coerce").fillna(0).astype(int)
original_data["COST"] = pd.to_numeric(original_data["COST"], errors="coerce").fillna(0)


@app.route("/")
def display_summary():
    # Render the table with editable QUANTITY column
    html_table = """
    <table class="table table-bordered table-hover" id="summary-table">
        <thead>
            <tr>
                """ + "".join([f"<th>{col}</th>" for col in original_data.columns]) + """
            </tr>
        </thead>
        <tbody>
            """ + "".join(
        [
            f"<tr>"
            + "".join(
                [
                    f'<td contenteditable="true" class="editable quantity">{row[col]}</td>'
                    if col == "QUANTITY"
                    else f'<td class="cost">{row[col]}</td>'
                    if col == "COST"
                    else f"<td>{row[col]}</td>"
                    for col in original_data.columns
                ]
            )
            + "</tr>"
            for _, row in original_data.iterrows()
        ]
    ) + """
        </tbody>
    </table>
    """

    # HTML Template
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
        <title>Editable Summary</title>
    </head>
    <body class="p-4">
        <h1>Summary Sheet</h1>
        <div id="table-container">
            {{ html_table | safe }}
        </div>
        <p><strong>Total Cost:</strong> <span id="total-cost">0</span></p>
        <button type="button" class="btn btn-primary" id="calculate-btn">Calculate</button>
        <button type="button" class="btn btn-secondary" id="reset-btn">Reset</button>

        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <script>
            // Calculate button functionality
            $('#calculate-btn').on('click', function () {
                let totalCost = 0;

                // Loop through QUANTITY and COST rows
                $('#summary-table tbody tr').each(function () {
                    const quantity = parseFloat($(this).find('.quantity').text()) || 0;
                    const cost = parseFloat($(this).find('.cost').text()) || 0;

                    totalCost += quantity * cost;
                });

                // Update total cost in the DOM
                $('#total-cost').text(totalCost.toFixed(2));
            });

            // Reset button functionality
            $('#reset-btn').on('click', function () {
                $.ajax({
                    url: "/reset",
                    method: "GET",
                    success: function (response) {
                        $('#table-container').html(response.table_html);
                        $('#total-cost').text(response.total_cost.toFixed(2));
                    }
                });
            });

            // Initial total cost calculation
            $('#calculate-btn').click();
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template, html_table=html_table)


@app.route("/reset", methods=["GET"])
def reset_summary():
    # Reset the table to its original state
    html_table = """
    <table class="table table-bordered table-hover" id="summary-table">
        <thead>
            <tr>
                """ + "".join([f"<th>{col}</th>" for col in original_data.columns]) + """
            </tr>
        </thead>
        <tbody>
            """ + "".join(
        [
            f"<tr>"
            + "".join(
                [
                    f'<td contenteditable="true" class="editable quantity">{row[col]}</td>'
                    if col == "QUANTITY"
                    else f'<td class="cost">{row[col]}</td>'
                    if col == "COST"
                    else f"<td>{row[col]}</td>"
                    for col in original_data.columns
                ]
            )
            + "</tr>"
            for _, row in original_data.iterrows()
        ]
    ) + """
        </tbody>
    </table>
    """
    total_cost = (original_data["QUANTITY"] * original_data["COST"]).sum()

    return jsonify({"table_html": html_table, "total_cost": total_cost})


if __name__ == "__main__":
    app.run(debug=True)
