from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def index():
	return render_template("index.html")

@app.route("/result", methods=["POST"])
def result():
	resume = request.form["resume"].lower()
	job_description = request.form["job-description"].lower()
	resume_words = set(resume.split())
	job_description_words = set(job_description.split())
	match_percentage = round(len(resume_words.intersection(job_description_words)) / len(job_description_words) * 100, 2)
	return render_template("result.html", match_percentage=match_percentage)

if __name__ == "__main__":
	app.run(port=3030)