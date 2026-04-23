import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle, Patch

# Experiment parameters
NUM_TESTS = 18
MEASUREMENT_TIMEPOINTS = [1, 15, 30, 60, 120, 240, 1440]  # minutes from test start
MEASUREMENT_DURATION = 6  # minutes each measurement takes

class ExperimentScheduler:
    def __init__(self, num_tests, timepoints, measurement_duration, max_test_duration=420):
        self.num_tests = num_tests
        self.timepoints = sorted(timepoints)
        self.measurement_duration = measurement_duration
        self.max_test_duration = max_test_duration  # Maximum minutes from start of test to last critical timepoint (e.g., 240 min)
        self.critical_timepoint = 240  # The critical timepoint that must complete by max_test_duration
    
    def get_measurement_windows(self, test_id, test_start_time):
        """
        Get all measurement time windows for a test.
        Returns list of (start, end) tuples for when gasmet is busy.
        """
        windows = []
        for timepoint in self.timepoints:
            meas_start = test_start_time + timepoint
            meas_end = meas_start + self.measurement_duration
            windows.append((meas_start, meas_end, test_id, timepoint))
        return windows
    
    def windows_overlap(self, window1, window2):
        """Check if two measurement windows overlap."""
        start1, end1 = window1[:2]
        start2, end2 = window2[:2]
        return not (end1 <= start2 or end2 <= start1)
    
    def find_valid_schedule_greedy(self):
        """
        Greedily assign test start times, trying to fit each test as early as possible
        without creating measurement conflicts.
        
        Constraint: Only schedule tests where the critical timepoint (240 min) occurs
        before the max_test_duration (420 min).
        """
        test_starts = []
        all_windows = []
        
        for test_id in range(self.num_tests):
            # Find the earliest start time for this test that doesn't conflict
            earliest_start = 0
            valid = False
            
            while not valid:
                # Check if this test would violate the max duration constraint
                critical_time = earliest_start + self.critical_timepoint
                if critical_time > self.max_test_duration:
                    # This test and all subsequent tests cannot be scheduled
                    print(f"\nReached scheduling limit: Test {test_id+1} would exceed {self.max_test_duration}-minute window")
                    print(f"(240-min timepoint would occur at {critical_time} min, but limit is {self.max_test_duration} min)")
                    return test_starts, all_windows
                
                test_windows = self.get_measurement_windows(test_id, earliest_start)
                
                # Check if any windows conflict with existing measurements
                conflict = False
                for new_window in test_windows:
                    for existing_window in all_windows:
                        if self.windows_overlap(new_window, existing_window):
                            conflict = True
                            break
                    if conflict:
                        break
                
                if not conflict:
                    # This start time works!
                    valid = True
                    test_starts.append(earliest_start)
                    all_windows.extend(test_windows)
                else:
                    # Try next minute
                    earliest_start += 1
        
        return test_starts, all_windows
    
    def calculate_schedule_from_starts(self, test_starts):
        """Given start times, generate the full schedule."""
        all_windows = []
        for test_id, test_start in enumerate(test_starts):
            windows = self.get_measurement_windows(test_id, test_start)
            all_windows.extend(windows)
        
        # Sort by measurement start time
        all_windows.sort(key=lambda x: x[0])
        
        schedule = []
        for start, end, test_id, timepoint in all_windows:
            schedule.append({
                'test_id': test_id,
                'timepoint': timepoint,
                'meas_start': start,
                'meas_end': end,
                'duration': end - start
            })
        
        return schedule
    
    def calculate_metrics(self, test_starts, schedule):
        """Calculate metrics for a schedule."""
        if not schedule:
            return {}
        
        total_time = max(m['meas_end'] for m in schedule)
        
        metrics = {
            'total_time_minutes': total_time,
            'total_time_hours': total_time / 60,
            'total_time_days': total_time / (24 * 60)
        }
        return metrics
    
    def create_constraint_visualization(self, test_starts, filename='constraint_analysis.png'):
        """Create a visualization showing which tests satisfy the constraint."""
        try:
            fig, ax = plt.subplots(figsize=(14, 8))
            
            # Calculate critical timepoints for all 18 tests
            all_test_ids = []
            all_critical_times = []
            all_colors = []
            all_margins = []
            
            for test_id in range(self.num_tests):
                all_test_ids.append(test_id + 1)
                
                if test_id < len(test_starts):
                    start_time = test_starts[test_id]
                    critical_time = start_time + self.critical_timepoint
                else:
                    # Tests that couldn't be scheduled
                    critical_time = None
                
                if critical_time is not None:
                    all_critical_times.append(critical_time)
                    margin = self.max_test_duration - critical_time
                    all_margins.append(margin)
                    
                    if critical_time <= self.max_test_duration:
                        all_colors.append('#27ae60')  # Green for scheduled
                    else:
                        all_colors.append('#e74c3c')  # Red for rejected
                else:
                    all_critical_times.append(0)
                    all_margins.append(-999)
                    all_colors.append('#95a5a6')  # Gray for unschedulable
            
            # Create bar chart
            bars = ax.barh(all_test_ids, all_critical_times, color=all_colors, alpha=0.7, edgecolor='black', linewidth=1.5)
            
            # Add constraint line
            ax.axvline(x=self.max_test_duration, color='red', linestyle='--', linewidth=3, label=f'Constraint: {self.max_test_duration} min')
            
            # Add value labels on bars
            for i, (test_id, critical_time, margin) in enumerate(zip(all_test_ids, all_critical_times, all_margins)):
                if critical_time > 0:
                    status = "✓" if margin >= 0 else "✗"
                    label_text = f"{critical_time:.0f} min {status}"
                    ax.text(critical_time + 10, test_id, label_text, va='center', fontweight='bold', fontsize=9)
            
            # Formatting
            ax.set_xlabel('Time of 240-min Measurement End (minutes)', fontsize=12, fontweight='bold')
            ax.set_ylabel('Test ID', fontsize=12, fontweight='bold')
            ax.set_title('Constraint Analysis: Which Tests Fit Within 7-Hour Window?\n(Green = ✓ Scheduled | Red = ✗ Excluded)', 
                        fontsize=14, fontweight='bold', pad=20)
            ax.set_xlim(0, self.max_test_duration + 150)
            
            # Add grid
            ax.grid(True, axis='x', alpha=0.3, linestyle=':')
            
            # Add legend
            legend_elements = [
                Patch(facecolor='#27ae60', alpha=0.7, edgecolor='black', label='✓ Scheduled (fits in 7 hrs)'),
                Patch(facecolor='#e74c3c', alpha=0.7, edgecolor='black', label='✗ Excluded (exceeds 7 hrs)'),
                plt.Line2D([0], [0], color='red', linestyle='--', linewidth=3, label=f'420-minute limit')
            ]
            ax.legend(handles=legend_elements, loc='lower right', fontsize=11)
            
            plt.tight_layout()
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"Constraint analysis chart saved to '{filename}'")
            plt.close(fig)
            
        except Exception as e:
            print(f"\nError creating constraint visualization: {e}")
            import traceback
            traceback.print_exc()
    
    def create_gantt_chart(self, test_starts, schedule, filename='experiment_gantt.png'):
        """Create a Gantt chart visualization of the experiment schedule."""
        try:
            fig, ax = plt.subplots(figsize=(16, 10))
            
            # Get the total time
            total_time = max(m['meas_end'] for m in schedule)
            
            # Colors for visualization
            test_color = '#3498db'  # Blue for test chambers running
            measurement_color = '#e74c3c'  # Red for measurements
            
            # Plot each test
            for test_id, start_time in enumerate(test_starts):
                # Calculate when this test ends (last measurement ends)
                test_measurements = [m for m in schedule if m['test_id'] == test_id]
                if test_measurements:
                    test_end = max(m['meas_end'] for m in test_measurements)
                    
                    # Draw the test chamber timeline
                    ax.barh(test_id, test_end - start_time, left=start_time, 
                           height=0.6, color=test_color, alpha=0.3, edgecolor=test_color, linewidth=1)
                    
                    # Draw measurement windows on top
                    for measurement in test_measurements:
                        meas_start = measurement['meas_start']
                        meas_duration = measurement['duration']
                        ax.barh(test_id, meas_duration, left=meas_start, 
                               height=0.4, color=measurement_color, alpha=0.7, edgecolor='darkred', linewidth=0.5)
                        
                        # Add timepoint label
                        label_x = meas_start + meas_duration / 2
                        ax.text(label_x, test_id, f"{measurement['timepoint']}'", 
                               ha='center', va='center', fontsize=7, fontweight='bold', color='white')
            
            # Formatting
            ax.set_ylim(-0.5, self.num_tests - 0.5)
            ax.set_xlim(0, total_time)
            ax.set_xlabel('Time (minutes)', fontsize=12, fontweight='bold')
            ax.set_ylabel('Test ID', fontsize=12, fontweight='bold')
            ax.set_title('Experiment Schedule Gantt Chart\n(Blue bars: test chambers running | Red bars: gasmet measurements)', 
                        fontsize=14, fontweight='bold', pad=20)
            ax.set_yticks(range(self.num_tests))
            ax.set_yticklabels([f'Test {i+1}' for i in range(self.num_tests)])
            
            # Add grid
            ax.grid(True, axis='x', alpha=0.3, linestyle='--')
            
            # Add legend
            legend_elements = [
                mpatches.Patch(facecolor=test_color, alpha=0.3, edgecolor=test_color, label='Test chamber active'),
                mpatches.Patch(facecolor=measurement_color, alpha=0.7, edgecolor='darkred', label='Gasmet measurement (6 min)')
            ]
            ax.legend(handles=legend_elements, loc='upper right', fontsize=10)
            
            # Tight layout
            plt.tight_layout()
            
            # Save
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"\nGantt chart saved to '{filename}'")
            plt.close(fig)
            
            return fig, ax
        except Exception as e:
            print(f"\nError creating Gantt chart: {e}")
            import traceback
            traceback.print_exc()


def find_optimal_schedule():
    """Find the optimal schedule using greedy algorithm."""
    scheduler = ExperimentScheduler(
        NUM_TESTS, 
        MEASUREMENT_TIMEPOINTS, 
        MEASUREMENT_DURATION,
        max_test_duration=420  # 7 hours max
    )
    
    print("=" * 80)
    print("EXPERIMENT SCHEDULING OPTIMIZATION")
    print("=" * 80)
    print(f"\nTotal tests: {NUM_TESTS}")
    print(f"Measurement timepoints per test: {MEASUREMENT_TIMEPOINTS}")
    print(f"Measurement duration: {MEASUREMENT_DURATION} minutes")
    print(f"Total measurements: {NUM_TESTS * len(MEASUREMENT_TIMEPOINTS)}")
    print(f"Continuous measurement time if no conflicts: {NUM_TESTS * len(MEASUREMENT_TIMEPOINTS) * MEASUREMENT_DURATION} minutes")
    print(f"\n*** CONSTRAINT: 240-min timepoint must complete by {scheduler.max_test_duration} minutes ***")
    
    print("\n" + "=" * 80)
    print("Finding optimal schedule using greedy algorithm...")
    print("=" * 80)
    
    test_starts, all_windows = scheduler.find_valid_schedule_greedy()
    schedule = scheduler.calculate_schedule_from_starts(test_starts)
    metrics = scheduler.calculate_metrics(test_starts, schedule)
    
    # Generate constraint analysis table
    print(f"\n" + "=" * 80)
    print("CONSTRAINT ANALYSIS - All Tests")
    print("=" * 80)
    print(f"{'Test':<6} {'Start (min)':<12} {'240-min at':<12} {'Status':<15} {'Margin':<12}")
    print("-" * 80)
    
    scheduled_tests = set(range(len(test_starts)))
    for test_id in range(NUM_TESTS):
        if test_id < len(test_starts):
            start_time = test_starts[test_id]
            critical_time = start_time + 240
            margin = scheduler.max_test_duration - critical_time
            status = "✓ SCHEDULED" if critical_time <= scheduler.max_test_duration else "✗ EXCLUDED"
            print(f"{test_id+1:<6} {start_time:<12.0f} {critical_time:<12.0f} {status:<15} {margin:+.0f} min")
        else:
            # Tests not scheduled - show they were rejected
            print(f"{test_id+1:<6} {'N/A':<12} {'N/A':<12} {'✗ REJECTED':<15} {'-':<12}")
    
    print(f"\nTotal elapsed time: {metrics['total_time_minutes']:.1f} min")
    print(f"                  = {metrics['total_time_hours']:.2f} hours")
    print(f"                  = {metrics['total_time_days']:.3f} days")
    
    print(f"\nTests scheduled: {len(test_starts)}/{NUM_TESTS}")
    print(f"Tests excluded: {NUM_TESTS - len(test_starts)}/{NUM_TESTS}")
    
    print(f"\nTest start times (minutes from experiment start):")
    print("-" * 50)
    for test_id, start_time in enumerate(test_starts):
        print(f"Test {test_id+1:2d}: Start at {start_time:6.0f} min")
    
    print(f"\nDetailed measurement schedule:")
    print("-" * 80)
    print(f"{'Test':<5} {'Timepoint':<12} {'Meas Start':<12} {'Meas End':<12} {'Duration':<10}")
    print("-" * 80)
    for m in schedule:
        print(f"{m['test_id']+1:<5} {m['timepoint']:<12.0f} {m['meas_start']:<12.0f} "
              f"{m['meas_end']:<12.0f} {m['duration']:<10.0f}")
    
    # Generate constraint violation chart
    print("\n" + "=" * 80)
    print("Generating visualizations...")
    print("=" * 80)
    scheduler.create_constraint_visualization(test_starts)
    
    # Generate Gantt chart
    scheduler.create_gantt_chart(test_starts, schedule)
    
    # Export to CSV
    print("\nExporting schedule to CSV...")
    try:
        df = pd.DataFrame(schedule)
        df.to_csv('optimal_schedule.csv', index=False)
        print(f"Schedule saved to 'optimal_schedule.csv'")
    except PermissionError:
        print("Warning: Could not write to optimal_schedule.csv (file may be locked)")
    except Exception as e:
        print(f"Error saving CSV: {e}")
    
    return test_starts, schedule, metrics


if __name__ == "__main__":
    test_starts, schedule, metrics = find_optimal_schedule()
