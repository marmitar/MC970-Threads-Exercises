#include <iostream>
#include <random>
#include <sstream>

// Function to generate random numbers between -1 and 1
static double random_number() {
    static std::mt19937 gen(std::random_device {} ());
    static std::uniform_real_distribution<double> dis(-1.0, 1.0);
    return dis(gen);
}

// Function to estimate pi using the Monte Carlo method
static void calculate_pi(int &count, int &n_points, int num_iterations) {
    int hits = 0;
    for (int i = 0; i < num_iterations; ++i) {
        n_points++; // count every try

        double x = random_number();
        double y = random_number();

        if (x * x + y * y <= 1.0) {
            ++hits;
        }
    }

    count += hits;

    std::cout << "hits: " << hits << " of " << num_iterations << std::endl;
}

int main() {
    const int num_iterations = 30000000;

    int count = 0;
    int n_points = 0;

    for (int i = 0; i < NUM_THREADS; ++i) {
        calculate_pi(count, n_points, num_iterations / NUM_THREADS);
    }

    std::cout << "count: " << count << " of " << n_points << std::endl;
    double pi = 4.0 * (double)count / (double)num_iterations;
    std::cout << "Used " << n_points << " points to estimate pi: " << pi
                        << std::endl;

    if (n_points != num_iterations) {
        std::stringstream message;
        message << "Error: number of computed points (" << n_points << ") does not"
            << " match the expected number of iterations (" << num_iterations << ")";
        throw std::logic_error(message.str());
    }

    return 0;
}
