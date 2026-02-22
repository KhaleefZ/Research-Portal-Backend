import pandas as pd
import io
import logging
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment

logger = logging.getLogger(__name__)

def generate_excel_file(data: list, debug_info: str = None) -> io.BytesIO:
    """Converts extracted financial data into formatted Excel file matching reference format.
    
    Format matches the example: Particulars in column B, multiple year columns
    
    Args:
        data: List of financial records with line_item, value, unit, period
        debug_info: Optional debugging information
        
    Returns:
        BytesIO buffer containing formatted Excel file
    """
    
    if not data or not isinstance(data, list):
        # Create error report
        logger.warning("No financial data. Creating error report.")
        error_df = pd.DataFrame([{
            "Particulars": "⚠️ No Data Found",
            "Status": "Unable to identify financial tables. Possible causes:",
            "Details": "• PDF is image-based (scanned document)\n• No financial data in document\n• Unrecognized table format",
            "Recommendation": "Please verify document contains financial statements"
        }])
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            error_df.to_excel(writer, sheet_name='Error', index=False)
        output.seek(0)
        return output
    
    # STEP 1: Organize data by metric name and period
    logger.info(f"Processing {len(data)} financial records for Excel export")
    
    # Group by metric name
    metrics_dict = {}
    all_periods = set()
    
    for record in data:
        line_item = record['line_item']
        value = record['value']
        period = record['period']
        
        all_periods.add(period)
        
        if line_item not in metrics_dict:
            metrics_dict[line_item] = {}
        
        metrics_dict[line_item][period] = value
    
    # STEP 2: Create pivot table DataFrame
    # Format: Column A (empty), Column B (Particulars), then columns for each year/period
    
    periods_sorted = sorted(list(all_periods), reverse=True)  # Latest first
    
    rows = []
    for metric_name, period_values in metrics_dict.items():
        row = {'Particulars': metric_name}
        
        # Add value for each period
        for period in periods_sorted:
            row[period] = period_values.get(period, None)
        
        rows.append(row)
    
    # Create DataFrame with proper column order
    column_order = ['Particulars'] + periods_sorted
    df = pd.DataFrame(rows)[column_order]
    
    logger.info(f"Created pivot table: {len(df)} metrics × {len(periods_sorted)} periods")
    
    # STEP 3: Write to Excel with formatting
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Financial_Analysis', index=False, startrow=0, startcol=0)
        
        workbook = writer.book
        worksheet = writer.sheets['Financial_Analysis']
        
        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4472C4',  # Professional blue
            'font_color': '#FFFFFF',  # White text
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 11
        })
        
        metric_format = workbook.add_format({
            'border': 1,
            'align': 'left',
            'valign': 'vcenter',
            'font_size': 10
        })
        
        number_format = workbook.add_format({
            'border': 1,
            'align': 'right',
            'valign': 'vcenter',
            'num_format': '#,##0.00',
            'font_size': 10
        })
        
        # Apply header formatting
        for col_num, value in enumerate(df.columns.values):
            cell = worksheet.write(0, col_num, value, header_format)
        
        # Auto-adjust column widths
        worksheet.set_column(0, 0, 3)  # Empty column A (narrow)
        worksheet.set_column(1, 1, 35)  # Particulars column (wide)
        
        # Set numeric columns width
        for col_num in range(2, len(df.columns) + 1):
            worksheet.set_column(col_num - 1, col_num - 1, 15)
        
        # Apply data formatting
        for row_num, row_data in enumerate(df.values, start=1):
            for col_num, value in enumerate(row_data):
                if col_num == 0:
                    # Particulars column
                    worksheet.write(row_num, col_num, value, metric_format)
                else:
                    # Numeric columns
                    if isinstance(value, (int, float)):
                        worksheet.write(row_num, col_num, value, number_format)
                    else:
                        worksheet.write(row_num, col_num, value, metric_format)
    
    logger.info("Excel file generated successfully")
    output.seek(0)
    return output