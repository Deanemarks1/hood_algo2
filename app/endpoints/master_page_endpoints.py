@app.route("/show_master_page", methods=["POST"])
def show_master_page():
    return render_template("master_page.html")
