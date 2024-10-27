import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_architecture_diagram():
    fig, ax = plt.subplots(figsize=(12, 8))

    # Input Layer
    ax.add_patch(patches.Rectangle((1, 6), 2, 1, edgecolor='black', facecolor='lightgray'))
    ax.text(2, 6.5, 'Input Data\n(CSV File)', fontsize=12, ha='center')

    # Data Preprocessing Block
    ax.add_patch(patches.Rectangle((1, 4), 2, 2, edgecolor='black', facecolor='lightblue'))
    ax.text(2, 5.5, 'Data Preprocessing', fontsize=12, ha='center')
    ax.text(2, 5.0, '- Create Sequences', fontsize=10, ha='center')
    ax.text(2, 4.7, '- Train-Test Split', fontsize=10, ha='center')

    # Model Training Block
    ax.add_patch(patches.Rectangle((4, 4), 2, 2, edgecolor='black', facecolor='lightgreen'))
    ax.text(5, 5.5, 'Model Training', fontsize=12, ha='center')
    ax.text(5, 5.0, '- CNN Model', fontsize=10, ha='center')
    ax.text(5, 4.7, '- Random Forest', fontsize=10, ha='center')
    ax.text(5, 4.4, '- XGBoost', fontsize=10, ha='center')

    # Prediction Block
    ax.add_patch(patches.Rectangle((7, 6), 2, 1, edgecolor='black', facecolor='lightyellow'))
    ax.text(8, 6.5, 'Model Predictions\n(Individual)', fontsize=12, ha='center')

    # Evaluation Block
    ax.add_patch(patches.Rectangle((7, 4), 2, 1, edgecolor='black', facecolor='lightpink'))
    ax.text(8, 4.5, 'Model Evaluation\n(MAE, RMSE)', fontsize=12, ha='center')

    # Ensemble Model Block
    ax.add_patch(patches.Rectangle((4, 2), 2, 1.5, edgecolor='black', facecolor='lightcoral'))
    ax.text(5, 3.25, 'Ensemble Model', fontsize=12, ha='center')
    ax.text(5, 3.0, '- Stack Predictions', fontsize=10, ha='center')
    ax.text(5, 2.7, '- Final Model', fontsize=10, ha='center')

    # Final Evaluation Block
    ax.add_patch(patches.Rectangle((7, 2), 2, 1, edgecolor='black', facecolor='lightgray'))
    ax.text(8, 2.5, 'Final Evaluation\n(MAE, RMSE)', fontsize=12, ha='center')

    # Visualization Block
    ax.add_patch(patches.Rectangle((1, 1), 8, 0.8, edgecolor='black', facecolor='lightblue'))
    ax.text(5, 1.5, 'Visualizations', fontsize=12, ha='center')
    ax.text(5, 1.2, '- Training Loss', fontsize=10, ha='center')
    ax.text(5, 0.9, '- Predictions Plot', fontsize=10, ha='center')
    ax.text(5, 0.6, '- Metrics Bar Chart', fontsize=10, ha='center')

    # Connecting Arrows
    ax.arrow(2, 6, 0.7, -0.7, head_width=0.1, head_length=0.2, fc='black', ec='black')
    ax.arrow(2, 5, 0.7, -0.7, head_width=0.1, head_length=0.2, fc='black', ec='black')
    ax.arrow(3, 4.5, 1, 0, head_width=0.1, head_length=0.2, fc='black', ec='black')
    ax.arrow(6, 6, 0.7, -0.7, head_width=0.1, head_length=0.2, fc='black', ec='black')
    ax.arrow(6, 4.5, 0.7, -0.7, head_width=0.1, head_length=0.2, fc='black', ec='black')
    ax.arrow(5, 2.5, 0.5, -1.5, head_width=0.1, head_length=0.2, fc='black', ec='black')
    ax.arrow(8, 2.5, 0.5, -1.5, head_width=0.1, head_length=0.2, fc='black', ec='black')
    
    ax.axis('off')
    plt.title('Architecture Diagram for Water Usage Prediction Model', fontsize=16)
    plt.tight_layout()
    plt.show()

draw_architecture_diagram()
