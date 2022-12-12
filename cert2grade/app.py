from flask import Flask, render_template
app = Flask('cert2grade')



if __name__ == '__main__':
    app.run(debug=True)