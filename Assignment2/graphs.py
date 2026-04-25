import matplotlib.pyplot as plt


def plot_results(results):
    """
    Plots the results of the experiments.

    Args:
        results (dict): A dictionary containing the results of the experiments.
                        The keys are the number of workers and the values are
                        lists of execution times for each batch size.

    Returns:
        None
    """
    for workers, times in results.items():
        plt.plot(times, label=f'{workers} workers')
    
    plt.xlabel('Batch Size')
    plt.ylabel('Execution Time (seconds)')
    plt.title('Execution Time vs Batch Size for Different Numbers of Workers')
    plt.legend()
    plt.grid()
    plt.show()