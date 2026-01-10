#!/usr/bin/env python3
"""
create_demo_video.py

Creates an animated demo video showing the wire generation process step by step.
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import FancyBboxPatch, Circle
import matplotlib.patches as mpatches

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from wire.wire_path_creator_professional import (
    WirePathCreatorProfessional,
    SmoothingStrategy
)
from wire.clinical_validator import validate_wire_for_manufacturing


def create_bracket_positions():
    """Create realistic bracket positions for upper arch."""
    positions = [
        {'position': np.array([24.0, 2.0, 0.0]), 'visible': True, 'tooth_type': 'molar_2', 'tooth_num': 17},
        {'position': np.array([20.0, 6.0, 0.0]), 'visible': True, 'tooth_type': 'molar_1', 'tooth_num': 16},
        {'position': np.array([16.0, 11.0, 0.0]), 'visible': True, 'tooth_type': 'premolar_2', 'tooth_num': 15},
        {'position': np.array([12.5, 15.0, 0.0]), 'visible': True, 'tooth_type': 'premolar_1', 'tooth_num': 14},
        {'position': np.array([8.5, 19.0, 0.0]), 'visible': True, 'tooth_type': 'canine', 'tooth_num': 13},
        {'position': np.array([4.5, 22.0, 0.0]), 'visible': True, 'tooth_type': 'lateral', 'tooth_num': 12},
        {'position': np.array([1.5, 23.0, 0.0]), 'visible': True, 'tooth_type': 'central', 'tooth_num': 11},
        {'position': np.array([-1.5, 23.0, 0.0]), 'visible': True, 'tooth_type': 'central', 'tooth_num': 21},
        {'position': np.array([-4.5, 22.0, 0.0]), 'visible': True, 'tooth_type': 'lateral', 'tooth_num': 22},
        {'position': np.array([-8.5, 19.0, 0.0]), 'visible': True, 'tooth_type': 'canine', 'tooth_num': 23},
        {'position': np.array([-12.5, 15.0, 0.0]), 'visible': True, 'tooth_type': 'premolar_1', 'tooth_num': 24},
        {'position': np.array([-16.0, 11.0, 0.0]), 'visible': True, 'tooth_type': 'premolar_2', 'tooth_num': 25},
        {'position': np.array([-20.0, 6.0, 0.0]), 'visible': True, 'tooth_type': 'molar_1', 'tooth_num': 26},
        {'position': np.array([-24.0, 2.0, 0.0]), 'visible': True, 'tooth_type': 'molar_2', 'tooth_num': 27},
    ]
    return positions


def create_demo_video():
    """Create an animated demo video."""
    print("Creating demo video...")
    
    output_dir = "/home/ubuntu/orthodontic_wire_generator_latest/demo_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Get bracket positions
    brackets = create_bracket_positions()
    positions = np.array([b['position'] for b in brackets])
    arch_center = np.array([0.0, 12.0, 0.0])
    
    # Generate wire path
    wire_creator = WirePathCreatorProfessional(
        material_name="niti_superelastic",
        wire_size="0.016",
        base_resolution=100,
        smoothing_strategy=SmoothingStrategy.CURVATURE_FLOW
    )
    wire_path = wire_creator.create_professional_path(brackets, arch_center)
    report = wire_creator.get_quality_report()
    validation = validate_wire_for_manufacturing(wire_path, "niti_superelastic", "0.016")
    
    # Create figure
    fig, ax = plt.subplots(figsize=(14, 10))
    fig.patch.set_facecolor('#1a1a2e')
    ax.set_facecolor('#16213e')
    
    # Set up axes
    ax.set_xlim(-35, 35)
    ax.set_ylim(-10, 35)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.2, color='white')
    ax.tick_params(colors='white')
    ax.spines['bottom'].set_color('white')
    ax.spines['top'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.spines['right'].set_color('white')
    
    # Title
    title = ax.set_title('Professional Orthodontic Wire Generation', 
                         fontsize=20, fontweight='bold', color='white', pad=20)
    
    # Initialize plot elements
    bracket_scatter = ax.scatter([], [], c='#00d4ff', s=150, marker='s', 
                                  label='Brackets', zorder=5, edgecolors='white', linewidths=2)
    wire_line, = ax.plot([], [], '#ff6b6b', linewidth=3, label='Wire Path', zorder=4)
    
    # Status text box
    status_box = ax.text(0.02, 0.98, '', transform=ax.transAxes, 
                         verticalalignment='top', fontsize=12, color='white',
                         bbox=dict(boxstyle='round,pad=0.5', facecolor='#0f3460', 
                                   edgecolor='#00d4ff', alpha=0.9),
                         family='monospace')
    
    # Quality metrics box
    metrics_box = ax.text(0.98, 0.98, '', transform=ax.transAxes,
                          verticalalignment='top', horizontalalignment='right',
                          fontsize=11, color='white',
                          bbox=dict(boxstyle='round,pad=0.5', facecolor='#0f3460',
                                    edgecolor='#00d4ff', alpha=0.9),
                          family='monospace')
    
    # Legend
    legend = ax.legend(loc='lower right', facecolor='#0f3460', edgecolor='#00d4ff',
                       labelcolor='white', fontsize=11)
    
    # Animation frames
    total_frames = 150
    bracket_appear_frames = 30
    wire_draw_frames = 80
    final_frames = 40
    
    def init():
        bracket_scatter.set_offsets(np.empty((0, 2)))
        wire_line.set_data([], [])
        status_box.set_text('')
        metrics_box.set_text('')
        return bracket_scatter, wire_line, status_box, metrics_box
    
    def animate(frame):
        # Phase 1: Show brackets appearing one by one
        if frame < bracket_appear_frames:
            progress = frame / bracket_appear_frames
            num_brackets = int(progress * len(positions))
            if num_brackets > 0:
                bracket_scatter.set_offsets(positions[:num_brackets, :2])
            
            status_box.set_text(f"Step 1: Loading Brackets\n"
                               f"Detected: {num_brackets}/{len(positions)}")
            metrics_box.set_text('')
            title.set_text('Loading Dental Model...')
        
        # Phase 2: Draw wire progressively
        elif frame < bracket_appear_frames + wire_draw_frames:
            bracket_scatter.set_offsets(positions[:, :2])
            
            wire_progress = (frame - bracket_appear_frames) / wire_draw_frames
            num_wire_points = int(wire_progress * len(wire_path))
            
            if num_wire_points > 1:
                wire_line.set_data(wire_path[:num_wire_points, 0], 
                                   wire_path[:num_wire_points, 1])
            
            status_box.set_text(f"Step 2: Generating Wire Path\n"
                               f"Material: NiTi Superelastic\n"
                               f"Size: 0.016 inch\n"
                               f"Progress: {int(wire_progress * 100)}%")
            
            if wire_progress > 0.5:
                current_length = wire_progress * report['path_length_mm']
                metrics_box.set_text(f"Wire Length: {current_length:.1f} mm")
            
            title.set_text('Generating Professional Wire Path...')
        
        # Phase 3: Show final results
        else:
            bracket_scatter.set_offsets(positions[:, :2])
            wire_line.set_data(wire_path[:, 0], wire_path[:, 1])
            
            status_box.set_text(f"✓ Wire Generation Complete\n\n"
                               f"Material: {wire_creator.material.name}\n"
                               f"Wire Size: 0.016 inch\n"
                               f"Smoothing: Curvature Flow")
            
            metrics_box.set_text(f"Quality Score: {validation.overall_score:.0f}/100\n"
                                f"Status: {'✓ VALID' if validation.is_valid else '✗ INVALID'}\n"
                                f"─────────────────\n"
                                f"Wire Length: {report['path_length_mm']:.1f} mm\n"
                                f"Min Radius: {report['metrics']['min_bend_radius_mm']:.2f} mm\n"
                                f"Smoothness: {report['metrics']['smoothness_score']:.0f}/100")
            
            title.set_text('Professional Orthodontic Wire Generation - Complete')
        
        return bracket_scatter, wire_line, status_box, metrics_box, title
    
    # Create animation
    anim = animation.FuncAnimation(fig, animate, init_func=init,
                                   frames=total_frames, interval=50, blit=False)
    
    # Save as MP4
    video_path = f"{output_dir}/wire_generation_demo.mp4"
    print(f"Saving video to {video_path}...")
    
    writer = animation.FFMpegWriter(fps=20, metadata=dict(artist='Manus AI'),
                                     bitrate=2000)
    anim.save(video_path, writer=writer, dpi=100)
    
    plt.close()
    print(f"Video saved: {video_path}")
    
    # Also save as GIF for wider compatibility
    gif_path = f"{output_dir}/wire_generation_demo.gif"
    print(f"Saving GIF to {gif_path}...")
    
    # Recreate animation for GIF
    fig, ax = plt.subplots(figsize=(14, 10))
    fig.patch.set_facecolor('#1a1a2e')
    ax.set_facecolor('#16213e')
    ax.set_xlim(-35, 35)
    ax.set_ylim(-10, 35)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.2, color='white')
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_color('white')
    
    title = ax.set_title('Professional Orthodontic Wire Generation', 
                         fontsize=20, fontweight='bold', color='white', pad=20)
    bracket_scatter = ax.scatter([], [], c='#00d4ff', s=150, marker='s', 
                                  label='Brackets', zorder=5, edgecolors='white', linewidths=2)
    wire_line, = ax.plot([], [], '#ff6b6b', linewidth=3, label='Wire Path', zorder=4)
    status_box = ax.text(0.02, 0.98, '', transform=ax.transAxes, 
                         verticalalignment='top', fontsize=12, color='white',
                         bbox=dict(boxstyle='round,pad=0.5', facecolor='#0f3460', 
                                   edgecolor='#00d4ff', alpha=0.9),
                         family='monospace')
    metrics_box = ax.text(0.98, 0.98, '', transform=ax.transAxes,
                          verticalalignment='top', horizontalalignment='right',
                          fontsize=11, color='white',
                          bbox=dict(boxstyle='round,pad=0.5', facecolor='#0f3460',
                                    edgecolor='#00d4ff', alpha=0.9),
                          family='monospace')
    ax.legend(loc='lower right', facecolor='#0f3460', edgecolor='#00d4ff',
              labelcolor='white', fontsize=11)
    
    anim = animation.FuncAnimation(fig, animate, init_func=init,
                                   frames=total_frames, interval=50, blit=False)
    
    anim.save(gif_path, writer='pillow', fps=15, dpi=80)
    plt.close()
    print(f"GIF saved: {gif_path}")
    
    return video_path, gif_path


if __name__ == "__main__":
    video_path, gif_path = create_demo_video()
    print(f"\nDemo files created:")
    print(f"  Video: {video_path}")
    print(f"  GIF: {gif_path}")
