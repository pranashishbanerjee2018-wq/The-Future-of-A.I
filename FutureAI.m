%% THE FUTURE OF ARTIFICIAL INTELLIGENCE
%% MATLAB Scientific Machine Learning Demonstration Script
%% Script: FutureAI.m
%% Objective: Supervised k-Nearest Neighbors (k-NN) Classification
%% Execution Mode: MATLAB Batch / Subprocess Engine

function FutureAI()
    fprintf('====================================================================\n');
    fprintf('  THE FUTURE OF ARTIFICIAL INTELLIGENCE - SCIENTIFIC DEMONSTRATION  \n');
    fprintf('  Module: Supervised Nearest-Neighbor Manifold Classifier           \n');
    fprintf('  Engine: MathWorks MATLAB Desktop Kernel Execution                 \n');
    fprintf('====================================================================\n\n');

    % Set reproducible random seed
    rng(42, 'twister');

    % 1. Determine Output Paths
    script_dir = fileparts(mfilename('fullpath'));
    if isempty(script_dir)
        script_dir = pwd;
    end
    results_dir = fullfile(script_dir, 'results');
    if ~exist(results_dir, 'dir')
        mkdir(results_dir);
    end

    % 2. Generate Synthetic 2D Classification Dataset
    % Two classes representing AI pattern recognition:
    % Class 0: Baseline Algorithmic State
    % Class 1: Emergent Cognitive State
    N_per_class = 100;
    
    % Class 0: Centered at [-1.2, -1.0] with covariance
    mu_0 = [-1.2, -1.0];
    sigma_0 = [0.8, 0.25; 0.25, 0.9];
    R_0 = chol(sigma_0);
    X_0 = randn(N_per_class, 2) * R_0 + repmat(mu_0, N_per_class, 1);
    y_0 = zeros(N_per_class, 1);

    % Class 1: Centered at [1.3, 1.2] with covariance
    mu_1 = [1.3, 1.2];
    sigma_1 = [0.85, -0.3; -0.3, 0.85];
    R_1 = chol(sigma_1);
    X_1 = randn(N_per_class, 2) * R_1 + repmat(mu_1, N_per_class, 1);
    y_1 = ones(N_per_class, 1);

    % Combine dataset
    X_all = [X_0; X_1];
    y_all = [y_0; y_1];
    N_total = size(X_all, 1);

    % Shuffle indices reproducibly
    shuffled_idx = randperm(N_total);
    X_all = X_all(shuffled_idx, :);
    y_all = y_all(shuffled_idx, :);

    % 3. Partition Data into Training (70%) and Testing (30%)
    split_ratio = 0.70;
    N_train = round(split_ratio * N_total);
    N_test = N_total - N_train;

    X_train = X_all(1:N_train, :);
    y_train = y_all(1:N_train, :);

    X_test = X_all(N_train+1:end, :);
    y_test = y_all(N_train+1:end, :);

    fprintf('[STEP 1] Dataset Partitioning:\n');
    fprintf('  Total Samples : %d (Feature 1: Activation Energy, Feature 2: Synaptic Coherence)\n', N_total);
    fprintf('  Training Set  : %d samples (70%%)\n', N_train);
    fprintf('  Testing Set   : %d samples (30%%)\n\n', N_test);

    % 4. Direct Supervised k-NN Classification (k = 3)
    % Implemented purely via base Euclidean distance matrix operations
    k_neighbors = 3;
    y_pred = zeros(N_test, 1);

    for i = 1:N_test
        test_pt = X_test(i, :);
        % Vectorized Euclidean distance calculation
        diff_mat = X_train - repmat(test_pt, N_train, 1);
        dist_sq = sum(diff_mat .^ 2, 2);
        [~, sorted_idx] = sort(dist_sq, 'ascend');
        nearest_labels = y_train(sorted_idx(1:k_neighbors));
        % Majority vote
        y_pred(i) = mode(nearest_labels);
    end

    % 5. Quantitative Model Evaluation
    correct_mask = (y_pred == y_test);
    num_correct = sum(correct_mask);
    accuracy = (num_correct / N_test) * 100.0;

    TP = sum((y_test == 1) & (y_pred == 1));
    TN = sum((y_test == 0) & (y_pred == 0));
    FP = sum((y_test == 0) & (y_pred == 1));
    FN = sum((y_test == 1) & (y_pred == 0));

    precision = TP / max(1, (TP + FP));
    recall = TP / max(1, (TP + FN));
    f1_score = 2 * (precision * recall) / max(1e-6, (precision + recall));

    fprintf('[STEP 2] Scientific Classification Results:\n');
    fprintf('  Measured Accuracy : %.2f%% (%d / %d correct)\n', accuracy, num_correct, N_test);
    fprintf('  Precision         : %.4f\n', precision);
    fprintf('  Recall            : %.4f\n', recall);
    fprintf('  F1-Score          : %.4f\n', f1_score);
    fprintf('  Confusion Matrix  :\n');
    fprintf('    True Positives  (TP) : %d\n', TP);
    fprintf('    False Positives (FP) : %d\n', FP);
    fprintf('    True Negatives  (TN) : %d\n', TN);
    fprintf('    False Negatives (FN) : %d\n\n', FN);

    % 6. Visualization 1: Decision Boundary Landscape
    fprintf('[STEP 3] Rendering Scientific Visualizations...\n');
    
    fig1 = figure('Visible', 'off', 'Color', [0.05, 0.08, 0.14], 'Position', [100, 100, 900, 650]);
    ax1 = axes('Parent', fig1, 'Color', [0.07, 0.11, 0.19]);
    hold(ax1, 'on');

    % Compute grid for continuous boundary
    grid_res = 120;
    x_range = linspace(-3.8, 3.8, grid_res);
    y_range = linspace(-3.8, 3.8, grid_res);
    [XX, YY] = meshgrid(x_range, y_range);
    grid_pts = [XX(:), YY(:)];
    grid_preds = zeros(size(grid_pts, 1), 1);

    for g = 1:size(grid_pts, 1)
        pt = grid_pts(g, :);
        d_sq = sum((X_train - repmat(pt, N_train, 1)) .^ 2, 2);
        [~, s_idx] = sort(d_sq, 'ascend');
        grid_preds(g) = mode(y_train(s_idx(1:k_neighbors)));
    end
    ZZ = reshape(grid_preds, size(XX));

    % Plot subtle decision surface contour
    colormap(ax1, [0.08, 0.20, 0.35; 0.28, 0.12, 0.38]);
    contourf(ax1, XX, YY, ZZ, 1, 'LineColor', [0.2, 0.5, 0.8], 'LineWidth', 1.5, 'FaceAlpha', 0.45);

    % Scatter Training Points
    scatter(ax1, X_train(y_train == 0, 1), X_train(y_train == 0, 2), 48, ...
        'MarkerEdgeColor', [0.1, 0.8, 0.9], 'MarkerFaceColor', [0.0, 0.5, 0.7], ...
        'DisplayName', 'Train: Baseline Algorithmic (Class 0)');
    scatter(ax1, X_train(y_train == 1, 1), X_train(y_train == 1, 2), 48, ...
        'MarkerEdgeColor', [1.0, 0.4, 0.8], 'MarkerFaceColor', [0.7, 0.1, 0.5], ...
        'DisplayName', 'Train: Emergent Cognitive (Class 1)');

    % Scatter Testing Points (Correct vs Incorrect)
    correct_test_idx = find(correct_mask);
    incorrect_test_idx = find(~correct_mask);

    if ~isempty(correct_test_idx)
        scatter(ax1, X_test(correct_test_idx, 1), X_test(correct_test_idx, 2), 70, ...
            'Marker', 'o', 'MarkerEdgeColor', [0.2, 1.0, 0.4], 'LineWidth', 2.0, ...
            'DisplayName', sprintf('Test: Correct Predictions (N=%d)', length(correct_test_idx)));
    end
    if ~isempty(incorrect_test_idx)
        scatter(ax1, X_test(incorrect_test_idx, 1), X_test(incorrect_test_idx, 2), 90, ...
            'Marker', 'x', 'MarkerEdgeColor', [1.0, 0.2, 0.2], 'LineWidth', 2.5, ...
            'DisplayName', sprintf('Test: Misclassified (N=%d)', length(incorrect_test_idx)));
    end

    title(ax1, {'MATLAB AI CLASSIFIER: DECISION BOUNDARY & SAMPLE TOPOLOGY', ...
        sprintf('Algorithm: k-Nearest Neighbors (k=3) | Test Accuracy = %.2f%%', accuracy)}, ...
        'Color', [0.9, 0.95, 1.0], 'FontSize', 13, 'FontWeight', 'bold');
    xlabel(ax1, 'Feature 1: Neural Activation Energy (E_{act}) [Norm]', 'Color', [0.75, 0.85, 0.95], 'FontSize', 11);
    ylabel(ax1, 'Feature 2: Synaptic Coherence Index (C_{syn}) [Norm]', 'Color', [0.75, 0.85, 0.95], 'FontSize', 11);
    set(ax1, 'XColor', [0.4, 0.55, 0.7], 'YColor', [0.4, 0.55, 0.7], 'GridColor', [0.2, 0.3, 0.45], 'GridAlpha', 0.4);
    grid(ax1, 'on');
    axis(ax1, [-3.8, 3.8, -3.8, 3.8]);
    leg1 = legend(ax1, 'Location', 'northeast');
    set(leg1, 'TextColor', [0.9, 0.95, 1.0], 'Color', [0.08, 0.12, 0.22], 'EdgeColor', [0.25, 0.4, 0.6]);

    img1_path = fullfile(results_dir, 'matlab_decision_boundary.png');
    saveas(fig1, img1_path);
    close(fig1);
    fprintf('  Saved: %s\n', img1_path);

    % 7. Visualization 2: Confusion Matrix & Metrics Dashboard
    fig2 = figure('Visible', 'off', 'Color', [0.05, 0.08, 0.14], 'Position', [100, 100, 950, 480]);
    
    % Subplot 1: Confusion Matrix Heatmap
    ax2 = subplot(1, 2, 1, 'Parent', fig2, 'Color', [0.07, 0.11, 0.19]);
    cm_matrix = [TN, FP; FN, TP];
    imagesc(ax2, cm_matrix);
    colormap(ax2, [0.08, 0.15, 0.28; 0.12, 0.35, 0.55; 0.05, 0.6, 0.65; 0.2, 0.85, 0.6]);
    colorbar(ax2, 'Color', [0.8, 0.9, 1.0]);

    % Add text annotations inside cells
    cell_labels = {sprintf('TN = %d\n(%.1f%%)', TN, TN/N_test*100), sprintf('FP = %d\n(%.1f%%)', FP, FP/N_test*100); ...
                   sprintf('FN = %d\n(%.1f%%)', FN, FN/N_test*100), sprintf('TP = %d\n(%.1f%%)', TP, TP/N_test*100)};
    for r = 1:2
        for c = 1:2
            text(ax2, c, r, cell_labels{r, c}, 'HorizontalAlignment', 'center', ...
                'VerticalAlignment', 'middle', 'Color', [1.0, 1.0, 1.0], 'FontSize', 12, 'FontWeight', 'bold');
        end
    end
    set(ax2, 'XTick', [1, 2], 'XTickLabel', {'Pred Class 0', 'Pred Class 1'}, ...
             'YTick', [1, 2], 'YTickLabel', {'True Class 0', 'True Class 1'}, ...
             'XColor', [0.8, 0.9, 1.0], 'YColor', [0.8, 0.9, 1.0], 'FontSize', 10);
    title(ax2, {'TEST CONFUSION MATRIX', sprintf('Total Test Samples = %d', N_test)}, ...
        'Color', [0.9, 0.95, 1.0], 'FontSize', 12, 'FontWeight', 'bold');

    % Subplot 2: Metric Comparison Bars
    ax3 = subplot(1, 2, 2, 'Parent', fig2, 'Color', [0.07, 0.11, 0.19]);
    hold(ax3, 'on');
    metric_names = {'Accuracy', 'Precision', 'Recall', 'F1-Score'};
    metric_vals = [accuracy, precision * 100, recall * 100, f1_score * 100];
    bar_colors = [0.15, 0.75, 0.95; 0.35, 0.65, 1.0; 0.55, 0.45, 0.95; 0.85, 0.35, 0.8];
    
    for b = 1:4
        hb = bar(ax3, b, metric_vals(b), 0.55, 'FaceColor', bar_colors(b, :), 'EdgeColor', 'none');
        text(ax3, b, metric_vals(b) + 3, sprintf('%.1f%%', metric_vals(b)), ...
            'HorizontalAlignment', 'center', 'Color', [0.95, 0.98, 1.0], 'FontWeight', 'bold', 'FontSize', 10);
    end
    ylim(ax3, [0, 115]);
    set(ax3, 'XTick', 1:4, 'XTickLabel', metric_names, 'XColor', [0.8, 0.9, 1.0], 'YColor', [0.8, 0.9, 1.0]);
    grid(ax3, 'on');
    set(ax3, 'GridColor', [0.2, 0.3, 0.45], 'GridAlpha', 0.4);
    ylabel(ax3, 'Percentage Score (%)', 'Color', [0.75, 0.85, 0.95]);
    title(ax3, {'VALIDATION METRIC PROFILE', 'Supervised Generalization Performance'}, ...
        'Color', [0.9, 0.95, 1.0], 'FontSize', 12, 'FontWeight', 'bold');

    img2_path = fullfile(results_dir, 'matlab_performance_metrics.png');
    saveas(fig2, img2_path);
    close(fig2);
    fprintf('  Saved: %s\n', img2_path);

    % 8. Save Numerical Results to JSON
    json_path = fullfile(results_dir, 'matlab_results.json');
    json_fid = fopen(json_path, 'w');
    if json_fid ~= -1
        fprintf(json_fid, '{\n');
        fprintf(json_fid, '  "status": "success",\n');
        fprintf(json_fid, '  "engine": "MathWorks MATLAB Desktop",\n');
        fprintf(json_fid, '  "algorithm": "Supervised k-Nearest Neighbors (k=3)",\n');
        fprintf(json_fid, '  "timestamp": "%s",\n', datestr(now, 'yyyy-mm-dd HH:MM:SS'));
        fprintf(json_fid, '  "dataset": {\n');
        fprintf(json_fid, '    "total_samples": %d,\n', N_total);
        fprintf(json_fid, '    "features": ["Neural Activation Energy", "Synaptic Coherence Index"],\n');
        fprintf(json_fid, '    "classes": ["Baseline Algorithmic (0)", "Emergent Cognitive (1)"],\n');
        fprintf(json_fid, '    "train_samples": %d,\n', N_train);
        fprintf(json_fid, '    "test_samples": %d,\n', N_test);
        fprintf(json_fid, '    "split_ratio": %.2f\n', split_ratio);
        fprintf(json_fid, '  },\n');
        fprintf(json_fid, '  "metrics": {\n');
        fprintf(json_fid, '    "accuracy_pct": %.2f,\n', accuracy);
        fprintf(json_fid, '    "correct_count": %d,\n', num_correct);
        fprintf(json_fid, '    "incorrect_count": %d,\n', N_test - num_correct);
        fprintf(json_fid, '    "precision": %.4f,\n', precision);
        fprintf(json_fid, '    "recall": %.4f,\n', recall);
        fprintf(json_fid, '    "f1_score": %.4f\n', f1_score);
        fprintf(json_fid, '  },\n');
        fprintf(json_fid, '  "confusion_matrix": {\n');
        fprintf(json_fid, '    "true_positives": %d,\n', TP);
        fprintf(json_fid, '    "false_positives": %d,\n', FP);
        fprintf(json_fid, '    "true_negatives": %d,\n', TN);
        fprintf(json_fid, '    "false_negatives": %d\n', FN);
        fprintf(json_fid, '  },\n');
        fprintf(json_fid, '  "artifacts": {\n');
        fprintf(json_fid, '    "decision_boundary_plot": "matlab_decision_boundary.png",\n');
        fprintf(json_fid, '    "performance_metrics_plot": "matlab_performance_metrics.png",\n');
        fprintf(json_fid, '    "dataset_csv": "matlab_results.csv"\n');
        fprintf(json_fid, '  }\n');
        fprintf(json_fid, '}\n');
        fclose(json_fid);
        fprintf('  Saved JSON: %s\n', json_path);
    end

    % 9. Save Detailed Test Predictions to CSV
    csv_path = fullfile(results_dir, 'matlab_results.csv');
    csv_fid = fopen(csv_path, 'w');
    if csv_fid ~= -1
        fprintf(csv_fid, 'SampleID,Feature1_ActivationEnergy,Feature2_SynapticCoherence,GroundTruth,PredictedClass,Correct\n');
        for i = 1:N_test
            fprintf(csv_fid, '%d,%.4f,%.4f,%d,%d,%d\n', ...
                i, X_test(i, 1), X_test(i, 2), y_test(i), y_pred(i), correct_mask(i));
        end
        fclose(csv_fid);
        fprintf('  Saved CSV: %s\n', csv_path);
    end

    fprintf('\n====================================================================\n');
    fprintf('  MATLAB SCIENTIFIC DEMONSTRATION EXECUTED SUCCESSFULLY             \n');
    fprintf('====================================================================\n');
end
