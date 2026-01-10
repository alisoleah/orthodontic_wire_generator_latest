#!/usr/bin/env python3
"""
demo_wire_generation.py

Demo script for professional orthodontic wire generation.
Creates visualizations showing the wire generation process.
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from wire.wire_path_creator_professional import (
    WirePathCreatorProfessional,
    SmoothingStrategy
)
from wire.arch_form_optimizer import ArchFormOptimizer, ArchFormType
from wire.clinical_validator import validate_wire_for_manufacturing


def create_realistic_bracket_positions(arch_type='upper'):
    """Create realistic bracket positions for upper or lower arch."""
    if arch_type == 'upper':
        # Upper arch - wider, more parabolic
        positions = [
            # Right side (patient's right) - from molar to central
            {'position': np.array([24.0, 2.0, 0.0]), 'visible': True, 'tooth_type': 'molar_2', 'tooth_num': 17},
            {'position': np.array([20.0, 6.0, 0.0]), 'visible': True, 'tooth_type': 'molar_1', 'tooth_num': 16},
            {'position': np.array([16.0, 11.0, 0.0]), 'visible': True, 'tooth_type': 'premolar_2', 'tooth_num': 15},
            {'position': np.array([12.5, 15.0, 0.0]), 'visible': True, 'tooth_type': 'premolar_1', 'tooth_num': 14},
            {'position': np.array([8.5, 19.0, 0.0]), 'visible': True, 'tooth_type': 'canine', 'tooth_num': 13},
            {'position': np.array([4.5, 22.0, 0.0]), 'visible': True, 'tooth_type': 'lateral', 'tooth_num': 12},
            {'position': np.array([1.5, 23.0, 0.0]), 'visible': True, 'tooth_type': 'central', 'tooth_num': 11},
            # Left side - from central to molar
            {'position': np.array([-1.5, 23.0, 0.0]), 'visible': True, 'tooth_type': 'central', 'tooth_num': 21},
            {'position': np.array([-4.5, 22.0, 0.0]), 'visible': True, 'tooth_type': 'lateral', 'tooth_num': 22},
            {'position': np.array([-8.5, 19.0, 0.0]), 'visible': True, 'tooth_type': 'canine', 'tooth_num': 23},
            {'position': np.array([-12.5, 15.0, 0.0]), 'visible': True, 'tooth_type': 'premolar_1', 'tooth_num': 24},
            {'position': np.array([-16.0, 11.0, 0.0]), 'visible': True, 'tooth_type': 'premolar_2', 'tooth_num': 25},
            {'position': np.array([-20.0, 6.0, 0.0]), 'visible': True, 'tooth_type': 'molar_1', 'tooth_num': 26},
            {'position': np.array([-24.0, 2.0, 0.0]), 'visible': True, 'tooth_type': 'molar_2', 'tooth_num': 27},
        ]
    else:
        # Lower arch - narrower, more U-shaped
        positions = [
            {'position': np.array([22.0, 0.0, 0.0]), 'visible': True, 'tooth_type': 'molar_2', 'tooth_num': 47},
            {'position': np.array([18.0, 4.0, 0.0]), 'visible': True, 'tooth_type': 'molar_1', 'tooth_num': 46},
            {'position': np.array([14.0, 9.0, 0.0]), 'visible': True, 'tooth_type': 'premolar_2', 'tooth_num': 45},
            {'position': np.array([10.5, 13.0, 0.0]), 'visible': True, 'tooth_type': 'premolar_1', 'tooth_num': 44},
            {'position': np.array([7.0, 16.5, 0.0]), 'visible': True, 'tooth_type': 'canine', 'tooth_num': 43},
            {'position': np.array([3.5, 19.0, 0.0]), 'visible': True, 'tooth_type': 'lateral', 'tooth_num': 42},
            {'position': np.array([1.2, 20.0, 0.0]), 'visible': True, 'tooth_type': 'central', 'tooth_num': 41},
            {'position': np.array([-1.2, 20.0, 0.0]), 'visible': True, 'tooth_type': 'central', 'tooth_num': 31},
            {'position': np.array([-3.5, 19.0, 0.0]), 'visible': True, 'tooth_type': 'lateral', 'tooth_num': 32},
            {'position': np.array([-7.0, 16.5, 0.0]), 'visible': True, 'tooth_type': 'canine', 'tooth_num': 33},
            {'position': np.array([-10.5, 13.0, 0.0]), 'visible': True, 'tooth_type': 'premolar_1', 'tooth_num': 34},
            {'position': np.array([-14.0, 9.0, 0.0]), 'visible': True, 'tooth_type': 'premolar_2', 'tooth_num': 35},
            {'position': np.array([-18.0, 4.0, 0.0]), 'visible': True, 'tooth_type': 'molar_1', 'tooth_num': 36},
            {'position': np.array([-22.0, 0.0, 0.0]), 'visible': True, 'tooth_type': 'molar_2', 'tooth_num': 37},
        ]
    return positions


def create_demo_visualization():
    """Create a comprehensive demo visualization."""
    print("=" * 60)
    print("PROFESSIONAL ORTHODONTIC WIRE GENERATION DEMO")
    print("=" * 60)
    
    # Create output directory
    output_dir = "/home/ubuntu/orthodontic_wire_generator_latest/demo_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Step 1: Create bracket positions
    print("\n[Step 1] Loading bracket positions...")
    upper_brackets = create_realistic_bracket_positions('upper')
    lower_brackets = create_realistic_bracket_positions('lower')
    
    upper_positions = np.array([b['position'] for b in upper_brackets])
    lower_positions = np.array([b['position'] for b in lower_brackets])
    
    print(f"  Upper arch: {len(upper_brackets)} brackets")
    print(f"  Lower arch: {len(lower_brackets)} brackets")
    
    # Step 2: Initialize professional wire creator
    print("\n[Step 2] Initializing Professional Wire Creator...")
    wire_creator = WirePathCreatorProfessional(
        material_name="niti_superelastic",
        wire_size="0.016",
        base_resolution=100,
        smoothing_strategy=SmoothingStrategy.CURVATURE_FLOW
    )
    print(f"  Material: {wire_creator.material.name}")
    print(f"  Wire size: {wire_creator.wire_spec.diameter_mm:.4f} mm")
    print(f"  Min bend radius: {wire_creator.material.min_bend_radius_mm} mm")
    
    # Step 3: Generate wire paths
    print("\n[Step 3] Generating professional wire paths...")
    
    upper_center = np.array([0.0, 12.0, 0.0])
    lower_center = np.array([0.0, 10.0, 0.0])
    
    upper_wire = wire_creator.create_professional_path(upper_brackets, upper_center)
    upper_report = wire_creator.get_quality_report()
    
    wire_creator_lower = WirePathCreatorProfessional(
        material_name="niti_superelastic",
        wire_size="0.016",
        base_resolution=100,
        smoothing_strategy=SmoothingStrategy.CURVATURE_FLOW
    )
    lower_wire = wire_creator_lower.create_professional_path(lower_brackets, lower_center)
    lower_report = wire_creator_lower.get_quality_report()
    
    print(f"  Upper wire: {len(upper_wire)} points, {upper_report['path_length_mm']:.2f} mm")
    print(f"  Lower wire: {len(lower_wire)} points, {lower_report['path_length_mm']:.2f} mm")
    
    # Step 4: Validate wires
    print("\n[Step 4] Validating wire paths...")
    upper_validation = validate_wire_for_manufacturing(upper_wire, "niti_superelastic", "0.016")
    lower_validation = validate_wire_for_manufacturing(lower_wire, "niti_superelastic", "0.016")
    
    print(f"  Upper wire score: {upper_validation.overall_score:.1f}/100 - {'VALID' if upper_validation.is_valid else 'INVALID'}")
    print(f"  Lower wire score: {lower_validation.overall_score:.1f}/100 - {'VALID' if lower_validation.is_valid else 'INVALID'}")
    
    # Step 5: Create visualizations
    print("\n[Step 5] Creating visualizations...")
    
    # Figure 1: 2D Wire Path Comparison
    fig1, axes = plt.subplots(1, 2, figsize=(16, 8))
    fig1.suptitle('Professional Orthodontic Wire Generation', fontsize=16, fontweight='bold')
    
    # Upper arch
    ax1 = axes[0]
    ax1.set_title('Upper Arch Wire', fontsize=14)
    ax1.scatter(upper_positions[:, 0], upper_positions[:, 1], 
                c='blue', s=100, marker='s', label='Brackets', zorder=5)
    ax1.plot(upper_wire[:, 0], upper_wire[:, 1], 
             'r-', linewidth=2.5, label='Professional Wire', zorder=4)
    
    # Add bracket labels
    for b in upper_brackets:
        ax1.annotate(str(b['tooth_num']), 
                    (b['position'][0], b['position'][1] + 1.5),
                    ha='center', fontsize=8)
    
    ax1.set_xlabel('X (mm)')
    ax1.set_ylabel('Y (mm)')
    ax1.set_aspect('equal')
    ax1.legend(loc='lower right')
    ax1.grid(True, alpha=0.3)
    
    # Add quality info
    info_text = f"Score: {upper_validation.overall_score:.0f}/100\n"
    info_text += f"Length: {upper_report['path_length_mm']:.1f} mm\n"
    info_text += f"Min Radius: {upper_report['metrics']['min_bend_radius_mm']:.2f} mm"
    ax1.text(0.02, 0.98, info_text, transform=ax1.transAxes, 
             verticalalignment='top', fontsize=10,
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # Lower arch
    ax2 = axes[1]
    ax2.set_title('Lower Arch Wire', fontsize=14)
    ax2.scatter(lower_positions[:, 0], lower_positions[:, 1], 
                c='blue', s=100, marker='s', label='Brackets', zorder=5)
    ax2.plot(lower_wire[:, 0], lower_wire[:, 1], 
             'r-', linewidth=2.5, label='Professional Wire', zorder=4)
    
    for b in lower_brackets:
        ax2.annotate(str(b['tooth_num']), 
                    (b['position'][0], b['position'][1] + 1.5),
                    ha='center', fontsize=8)
    
    ax2.set_xlabel('X (mm)')
    ax2.set_ylabel('Y (mm)')
    ax2.set_aspect('equal')
    ax2.legend(loc='lower right')
    ax2.grid(True, alpha=0.3)
    
    info_text = f"Score: {lower_validation.overall_score:.0f}/100\n"
    info_text += f"Length: {lower_report['path_length_mm']:.1f} mm\n"
    info_text += f"Min Radius: {lower_report['metrics']['min_bend_radius_mm']:.2f} mm"
    ax2.text(0.02, 0.98, info_text, transform=ax2.transAxes, 
             verticalalignment='top', fontsize=10,
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    fig1.savefig(f"{output_dir}/wire_paths_2d.png", dpi=150, bbox_inches='tight')
    print(f"  Saved: {output_dir}/wire_paths_2d.png")
    
    # Figure 2: 3D Visualization
    fig2 = plt.figure(figsize=(14, 10))
    ax3d = fig2.add_subplot(111, projection='3d')
    ax3d.set_title('3D Wire Visualization - Both Arches', fontsize=14, fontweight='bold')
    
    # Upper arch (elevated)
    upper_wire_3d = upper_wire.copy()
    upper_wire_3d[:, 2] = 5  # Elevate upper arch
    upper_positions_3d = upper_positions.copy()
    upper_positions_3d[:, 2] = 5
    
    ax3d.scatter(upper_positions_3d[:, 0], upper_positions_3d[:, 1], upper_positions_3d[:, 2],
                c='blue', s=80, marker='s', label='Upper Brackets')
    ax3d.plot(upper_wire_3d[:, 0], upper_wire_3d[:, 1], upper_wire_3d[:, 2],
             'r-', linewidth=2, label='Upper Wire')
    
    # Lower arch
    ax3d.scatter(lower_positions[:, 0], lower_positions[:, 1], lower_positions[:, 2],
                c='green', s=80, marker='s', label='Lower Brackets')
    ax3d.plot(lower_wire[:, 0], lower_wire[:, 1], lower_wire[:, 2],
             'orange', linewidth=2, label='Lower Wire')
    
    ax3d.set_xlabel('X (mm)')
    ax3d.set_ylabel('Y (mm)')
    ax3d.set_zlabel('Z (mm)')
    ax3d.legend()
    
    fig2.savefig(f"{output_dir}/wire_paths_3d.png", dpi=150, bbox_inches='tight')
    print(f"  Saved: {output_dir}/wire_paths_3d.png")
    
    # Figure 3: Curvature Analysis
    fig3, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig3.suptitle('Wire Quality Analysis', fontsize=16, fontweight='bold')
    
    # Calculate curvatures
    def calculate_curvatures(path):
        curvatures = []
        for i in range(1, len(path) - 1):
            v1 = path[i] - path[i-1]
            v2 = path[i+1] - path[i]
            cross = np.cross(v1, v2)
            a = np.linalg.norm(v1)
            b = np.linalg.norm(v2)
            c = np.linalg.norm(path[i+1] - path[i-1])
            if a > 0 and b > 0 and c > 0:
                area = np.linalg.norm(cross) / 2
                if area > 1e-10:
                    radius = (a * b * c) / (4 * area)
                    curvatures.append(1/radius if radius > 0 else 0)
                else:
                    curvatures.append(0)
            else:
                curvatures.append(0)
        return np.array(curvatures)
    
    upper_curvatures = calculate_curvatures(upper_wire)
    lower_curvatures = calculate_curvatures(lower_wire)
    
    # Upper curvature plot
    ax = axes[0, 0]
    ax.plot(upper_curvatures, 'b-', linewidth=1.5)
    ax.axhline(y=1/wire_creator.material.min_bend_radius_mm, color='r', 
               linestyle='--', label=f'Max allowed (1/{wire_creator.material.min_bend_radius_mm}mm)')
    ax.set_title('Upper Wire Curvature')
    ax.set_xlabel('Point Index')
    ax.set_ylabel('Curvature (1/mm)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Lower curvature plot
    ax = axes[0, 1]
    ax.plot(lower_curvatures, 'g-', linewidth=1.5)
    ax.axhline(y=1/wire_creator.material.min_bend_radius_mm, color='r', 
               linestyle='--', label=f'Max allowed')
    ax.set_title('Lower Wire Curvature')
    ax.set_xlabel('Point Index')
    ax.set_ylabel('Curvature (1/mm)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Segment lengths
    upper_segments = np.linalg.norm(np.diff(upper_wire, axis=0), axis=1)
    lower_segments = np.linalg.norm(np.diff(lower_wire, axis=0), axis=1)
    
    ax = axes[1, 0]
    ax.hist(upper_segments, bins=20, color='blue', alpha=0.7, edgecolor='black')
    ax.axvline(x=np.mean(upper_segments), color='r', linestyle='--', 
               label=f'Mean: {np.mean(upper_segments):.2f}mm')
    ax.set_title('Upper Wire Segment Lengths')
    ax.set_xlabel('Segment Length (mm)')
    ax.set_ylabel('Count')
    ax.legend()
    
    ax = axes[1, 1]
    ax.hist(lower_segments, bins=20, color='green', alpha=0.7, edgecolor='black')
    ax.axvline(x=np.mean(lower_segments), color='r', linestyle='--', 
               label=f'Mean: {np.mean(lower_segments):.2f}mm')
    ax.set_title('Lower Wire Segment Lengths')
    ax.set_xlabel('Segment Length (mm)')
    ax.set_ylabel('Count')
    ax.legend()
    
    plt.tight_layout()
    fig3.savefig(f"{output_dir}/wire_quality_analysis.png", dpi=150, bbox_inches='tight')
    print(f"  Saved: {output_dir}/wire_quality_analysis.png")
    
    # Figure 4: Material Comparison
    fig4, ax = plt.subplots(figsize=(12, 8))
    ax.set_title('Wire Generation with Different Materials', fontsize=14, fontweight='bold')
    
    materials = ['niti_superelastic', 'tma', 'stainless_steel']
    colors = ['red', 'green', 'blue']
    
    for mat, color in zip(materials, colors):
        creator = WirePathCreatorProfessional(
            material_name=mat,
            wire_size="0.016",
            base_resolution=100,
            smoothing_strategy=SmoothingStrategy.CURVATURE_FLOW
        )
        wire = creator.create_professional_path(upper_brackets, upper_center)
        report = creator.get_quality_report()
        
        ax.plot(wire[:, 0], wire[:, 1], color=color, linewidth=2,
               label=f"{creator.material.name} (Score: {report['metrics']['smoothness_score']:.0f})")
    
    ax.scatter(upper_positions[:, 0], upper_positions[:, 1], 
              c='black', s=80, marker='s', label='Brackets', zorder=5)
    
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.set_aspect('equal')
    ax.legend(loc='lower right')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    fig4.savefig(f"{output_dir}/material_comparison.png", dpi=150, bbox_inches='tight')
    print(f"  Saved: {output_dir}/material_comparison.png")
    
    plt.close('all')
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)
    print(f"\nOutput files saved to: {output_dir}/")
    
    return {
        'upper_wire': upper_wire,
        'lower_wire': lower_wire,
        'upper_report': upper_report,
        'lower_report': lower_report,
        'output_dir': output_dir
    }


if __name__ == "__main__":
    result = create_demo_visualization()
