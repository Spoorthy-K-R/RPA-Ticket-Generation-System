# Import required libraries
import csv  # For reading CSV files
import matplotlib.pyplot as plt  # For creating plots

# Load data from CSV file
csv_filename = 'RPA_DATASET.csv'
csv_file = open(csv_filename, mode='r')
data_set = []

# Read and store category and subject information
for row in list(csv.DictReader(csv_file)):
    data_set.append({
        'category': row['CATEGORY'],
        'subject': row['REGARDING']
    })
csv_file.close()

# Initialize dictionaries to store statistics
stats_category = {}  # For category-wise counts
stats_subject = {}   # For subject-wise counts

# Calculate statistics
for row in data_set:
    # Count categories
    if (not row['category'] in stats_category.keys()):
        stats_category[row['category']] = 0
    stats_category[row['category']] += 1
    
    # Count subjects
    if (not row['subject'] in stats_subject.keys()):
        stats_subject[row['subject']] = 0
    stats_subject[row['subject']] += 1

# Print category statistics
print(stats_category)

def plot_dict(d):
    """
    Creates a bar plot from a dictionary of counts.
    
    Args:
        d (dict): Dictionary with categories/subjects as keys and counts as values
    """
    # Extract keys and values for plotting
    x, y = d.keys(), d.values()
    
    # Create bar plot
    plt.bar(x, y)
    
    # Adjust x-axis labels for better readability
    plt.xticks(fontsize='8')
    
    # Display the plot
    plt.show()

# Create plots for both category and subject statistics
plot_dict(stats_category)  # Plot category distribution
plot_dict(stats_subject)   # Plot subject distribution

