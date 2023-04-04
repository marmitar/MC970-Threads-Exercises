#include <algorithm>
#include <array>
#include <atomic>
#include <iostream>
#include <random>
#include <sstream>
#include <thread>


class RNG final {
private:
    using generator_t = std::mt19937_64;

    [[gnu::cold]]
    static auto random_seed() -> generator_t::result_type {
        using rd_limits = std::numeric_limits<std::random_device::result_type>;
        using rng_limits = std::numeric_limits<generator_t::result_type>;
        static_assert(std::random_device::max() == rd_limits::max(), "invalid random_device");

        constexpr auto SEED_SIZE = sizeof(generator_t::result_type);
        constexpr auto RDEV_SIZE = sizeof(std::random_device::result_type);

        std::random_device rdev;
        auto result = generator_t::result_type { 0 };

        constexpr auto NEEDED_RDEVS = (SEED_SIZE - 1) / RDEV_SIZE + 1;
        for (unsigned i = 0; i < NEEDED_RDEVS; i++) {
            result <<= static_cast<generator_t::result_type>(rd_limits::digits);
            result |= static_cast<generator_t::result_type>(rdev() & rng_limits::max());
        }
        return result;
    }

    generator_t generator { RNG::random_seed() };
    std::uniform_real_distribution<double> distribution { -1.0, 1.0 };

public:
    // Function to generate random numbers between -1 and 1
    [[gnu::hot]]
    auto random_number() -> double {
        return distribution(generator);
    }
};

// Function to estimate pi using the Monte Carlo method
template <unsigned num_iterations>
static void calculate_pi(std::atomic_uint &count, std::atomic_uint &n_points) {
    auto rng = RNG();

    unsigned hits = 0;
    for (unsigned i = 0; i < num_iterations; i++) {
        double x = rng.random_number();
        double y = rng.random_number();

        if (x * x + y * y <= 1.0) {
            hits++;
        }
    }

    n_points.fetch_add(num_iterations, std::memory_order_relaxed);
    count.fetch_add(hits, std::memory_order_relaxed);

    std::cout << "hits: " << hits << " of " << num_iterations << std::endl;
}

int main() {
    constexpr unsigned num_iterations = 30000000;

    std::atomic<unsigned> count { 0 };
    std::atomic<unsigned> n_points { 0 };
    std::array<std::thread, NUM_THREADS> threads;

    std::for_each(threads.begin(), threads.end(), [&](std::thread &thread) {
        constexpr unsigned iter_per_thread = num_iterations / NUM_THREADS;
        static_assert(iter_per_thread * NUM_THREADS == num_iterations, "invalid NUM_THREADS");

        thread = std::thread(calculate_pi<iter_per_thread>, std::ref(count), std::ref(n_points));
    });
    std::for_each(threads.begin(), threads.end(), [](std::thread &thread) {
        thread.join();
    });

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
    return EXIT_SUCCESS;
}
