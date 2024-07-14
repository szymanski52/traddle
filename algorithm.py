import matplotlib.pyplot as plt
import io
import base64
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

def calculate_metrics(actual_values, predictions):
    mse = mean_squared_error(actual_values, predictions)
    mae = mean_absolute_error(actual_values, predictions)
    r2 = r2_score(actual_values, predictions)
    return mse, mae, r2

def plot_predictions(ticker_times, actual_values, predictions, prediction_intervals):
    fig, ax = plt.subplots()
    ax.plot(ticker_times, actual_values, label='Actual', color='white')
    colors = {
        '1h': 'blue',
        '2h': 'green',
        '6h': 'orange',
        '24h': 'red',
        '3d': 'purple'
    }
    for interval in prediction_intervals:
        ax.plot(ticker_times, predictions[interval], label=f'{interval} Prediction', color=colors[interval])
    
    # Add legend
    ax.legend()
    ax.set_facecolor('black')
    fig.patch.set_facecolor('black')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    ax.spines['left'].set_color('white')
    ax.spines['bottom'].set_color('white')
    ax.yaxis.label.set_color('white')
    ax.xaxis.label.set_color('white')
    ax.title.set_color('white')
    
    img = io.BytesIO()
    plt.savefig(img, format='png', facecolor=fig.get_facecolor())
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    plt.close(fig)
    
    return plot_url
