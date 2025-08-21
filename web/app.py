from flask import Flask, render_template, request, redirect, url_for, flash
import os
import subprocess


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flash messages


@app.route("/", methods=["GET", "POST"])
def home():
    file_path = os.path.join(os.path.dirname(__file__), '..', 'auto_usbids.txt')
    content = ''
    output_lines = []
    data_cmd = ['/opt/usbip-server/ls_usbids.py']

    if request.method == 'POST':
        # Save action (only when Save button is pressed)
        if 'editor' in request.form and 'save' in request.form:
            content = request.form.get('editor', '')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            flash('File saved successfully!', 'success')
            # Re-run data_cmd for fresh output
            try:
                output_lines = subprocess.check_output(data_cmd, text=True).splitlines()
            except Exception as e:
                output_lines = [f"Error: {e}"]
        # Update data_cmd output
        elif 'update_data' in request.form:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            try:
                output_lines = subprocess.check_output(data_cmd, text=True).splitlines()
            except Exception as e:
                output_lines = [f"Error: {e}"]
        # Add line to editor (append, do not remove from data)
        elif 'add_line' in request.form:
            add_line = request.form.get('add_line')
            content = request.form.get('editor', '')
            # Ensure content ends with a single newline before appending
            if content and not content.endswith('\n'):
                content += '\n'
            elif not content:
                content = ''
            content += ' '.join(add_line.split()[6:])  #+ '\n'
            content = content.rstrip('\n') + '\n'  # Ensure only one newline at the end
            # Always update output_lines for UI refresh
            print(f"Adding line raw: {add_line}")
            print(f"content: {content}")
            try:
                output_lines = subprocess.check_output(data_cmd, text=True).splitlines()
            except Exception as e:
                output_lines = [f"Error: {e}"]
        else:
            # Fallback: just reload
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            try:
                output_lines = subprocess.check_output(data_cmd, text=True).splitlines()
            except Exception as e:
                output_lines = [f"Error: {e}"]
    else:
        # GET: load file and data_cmd output
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        try:
            output_lines = subprocess.check_output(data_cmd, text=True).splitlines()
        except Exception as e:
            output_lines = [f"Error: {e}"]

    # Join output lines for hidden field
    output_lines_str = '\n'.join(output_lines)

    # Get output for the right panel
    try:
        right_panel_output = '\n'.join(subprocess.check_output(['usbip', 'list', '--remote', 'localhost'], text=True).splitlines()[3:])
    except Exception as e:
        right_panel_output = f"Error: {e}"

    return render_template('home.html', content=content, output_lines=output_lines, output_lines_str=output_lines_str, right_panel_output=right_panel_output)



if __name__ == "__main__":
    app.run()
