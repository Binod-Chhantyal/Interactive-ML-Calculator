from flask import Flask, render_template, request, jsonify
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import io
import base64
import os

app = Flask(__name__)

def plot_histogram(nums):
    plt.figure()
    plt.hist(nums, bins=10, color='blue', alpha=0.7)
    plt.title('Histogram')
    plt.xlabel('Values')
    plt.ylabel('Frequency')
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return plot_url

def plot_regression(points):
    points = np.array(points)
    X = points[:, 0].reshape(-1, 1)
    y = points[:, 1]
    model = LinearRegression()
    model.fit(X, y)
    slope = model.coef_[0]
    intercept = model.intercept_

    plt.figure()
    plt.scatter(X, y)
    plt.plot(X, model.predict(X), color='red')
    plt.title('Linear Regression')
    plt.xlabel('X')
    plt.ylabel('Y')
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return slope, intercept, plot_url

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    operation = data.get('operation')
    input_text = data.get('input')

    # Helper to parse numbers (for 2-number ops)
    def parse_two_numbers(text):
        try:
            nums = list(map(float, text.strip().split()))
            if len(nums) != 2:
                return None
            return nums
        except:
            return None

    # Helper to parse pairs for regression/histogram
    def parse_pairs(text):
        try:
            pairs = text.strip().split()
            points = []
            for p in pairs:
                x_str, y_str = p.split(',')
                points.append([float(x_str), float(y_str)])
            return points
        except:
            return None

    if operation in ['add', 'subtract', 'multiply', 'divide']:
        nums = parse_two_numbers(input_text)
        if not nums:
            return jsonify({'error': 'Enter exactly two numbers separated by spaces.'}), 400

        if operation == 'add':
            result = nums[0] + nums[1]
        elif operation == 'subtract':
            result = nums[0] - nums[1]
        elif operation == 'multiply':
            result = nums[0] * nums[1]
        elif operation == 'divide':
            if nums[1] == 0:
                return jsonify({'error': 'Cannot divide by zero.'}), 400
            result = nums[0] / nums[1]

        return jsonify({'result': result})

    elif operation == 'histogram':
        points = parse_pairs(input_text)
        if not points:
            return jsonify({'error': 'Enter pairs like x,y separated by spaces.'}), 400
        # Extract just y-values for histogram to keep it simple
        y_values = [pt[1] for pt in points]
        plot_url = plot_histogram(y_values)
        return jsonify({'plot_url': plot_url})

    elif operation == 'linear_regression':
        points = parse_pairs(input_text)
        if not points or len(points) < 2:
            return jsonify({'error': 'Enter at least two pairs like x,y separated by spaces.'}), 400
        slope, intercept, plot_url = plot_regression(points)
        return jsonify({'slope': slope, 'intercept': intercept, 'plot_url': plot_url})

    else:
        return jsonify({'error': 'Invalid operation'}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))  # Render sets PORT env variable
    app.run(host='0.0.0.0', port=port, debug=True)
