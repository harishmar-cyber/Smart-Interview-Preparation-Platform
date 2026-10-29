// Interactive Coding Practice Engine

function initCodingEditor(problemId) {
    const editorTextarea = document.getElementById('codeEditorTextarea');
    const runSampleBtn = document.getElementById('runSampleTestsBtn');
    const submitCodeBtn = document.getElementById('submitSolutionBtn');
    const outputConsole = document.getElementById('executionOutputConsole');
    const testResultsContainer = document.getElementById('testResultsTabsContainer');

    if (!editorTextarea) return;

    // Enable Tab Indentation in Textarea
    editorTextarea.addEventListener('keydown', function(e) {
        if (e.key === 'Tab') {
            e.preventDefault();
            const start = this.selectionStart;
            const end = this.selectionEnd;
            this.value = this.value.substring(0, start) + '    ' + this.value.substring(end);
            this.selectionStart = this.selectionEnd = start + 4;
        }
    });

    // Run Sample Tests
    if (runSampleBtn) {
        runSampleBtn.addEventListener('click', async () => {
            const code = editorTextarea.value;
            if (!code.trim()) {
                showToast("Please write code before running tests.", "warning");
                return;
            }

            setLoadingState(runSampleBtn, true, "Running...");
            outputConsole.innerHTML = '<span class="text-secondary"><i class="fas fa-spinner fa-spin me-2"></i> Executing sample test cases...</span>';

            try {
                const response = await fetch(`/coding/${problemId}/run`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ code })
                });

                const data = await response.json();
                renderExecutionResults(data.result, false);
            } catch (err) {
                console.error(err);
                outputConsole.innerHTML = `<span class="text-danger">Network Error: Failed to execute code.</span>`;
            } finally {
                setLoadingState(runSampleBtn, false, '<i class="fas fa-play me-1"></i> Run Sample Tests');
            }
        });
    }

    // Submit Solution
    if (submitCodeBtn) {
        submitCodeBtn.addEventListener('click', async () => {
            const code = editorTextarea.value;
            if (!code.trim()) {
                showToast("Please write code before submitting.", "warning");
                return;
            }

            setLoadingState(submitCodeBtn, true, "Submitting...");
            outputConsole.innerHTML = '<span class="text-secondary"><i class="fas fa-spinner fa-spin me-2"></i> Evaluating against all test cases...</span>';

            try {
                const response = await fetch(`/coding/${problemId}/submit`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ code })
                });

                const data = await response.json();
                renderExecutionResults(data.result, true);

                if (data.result.result_status === 'Accepted') {
                    showToast("🎉 Excellent! All test cases passed! Solution Accepted.", "success");
                    const statusBadge = document.getElementById('problemStatusBadge');
                    if (statusBadge) {
                        statusBadge.className = 'badge bg-success-subtle text-success';
                        statusBadge.innerHTML = '<i class="fas fa-check-circle me-1"></i> Solved';
                    }
                } else {
                    showToast(`Evaluation Status: ${data.result.result_status}`, "danger");
                }
            } catch (err) {
                console.error(err);
                outputConsole.innerHTML = `<span class="text-danger">Submission Error: Unable to reach evaluation server.</span>`;
            } finally {
                setLoadingState(submitCodeBtn, false, '<i class="fas fa-cloud-upload-alt me-1"></i> Submit Solution');
            }
        });
    }

    function renderExecutionResults(result, isSubmission) {
        let statusBadgeClass = 'bg-secondary';
        if (result.result_status === 'Accepted') statusBadgeClass = 'bg-success';
        else if (result.result_status === 'Wrong Answer') statusBadgeClass = 'bg-danger';
        else if (result.result_status === 'Time Limit Exceeded') statusBadgeClass = 'bg-warning text-dark';
        else if (result.result_status === 'Runtime Error') statusBadgeClass = 'bg-danger';
        else if (result.result_status === 'Security Error') statusBadgeClass = 'bg-danger';

        let headerHtml = `
            <div class="d-flex align-items-center justify-content-between mb-3 pb-2 border-bottom border-secondary">
                <div class="d-flex align-items-center gap-2">
                    <span class="badge ${statusBadgeClass} fs-6 px-3 py-2">${result.result_status}</span>
                    <span class="text-white-50 ms-2">Passed <strong>${result.test_cases_passed} / ${result.test_cases_total}</strong> cases</span>
                </div>
                <div class="text-white-50">
                    <i class="far fa-clock me-1"></i> Runtime: <strong>${result.runtime_ms} ms</strong>
                </div>
            </div>
        `;

        if (result.error_message) {
            headerHtml += `
                <div class="alert alert-danger py-2 px-3 mb-3 font-monospace small">
                    <i class="fas fa-exclamation-triangle me-1"></i> ${escapeHtml(result.error_message)}
                </div>
            `;
        }

        let casesHtml = '<div class="row g-2">';
        result.test_results.forEach(tc => {
            const isPass = tc.passed;
            casesHtml += `
                <div class="col-12">
                    <div class="p-2 rounded ${isPass ? 'bg-success-subtle text-success-emphasis' : 'bg-danger-subtle text-danger-emphasis'} small border ${isPass ? 'border-success' : 'border-danger'}">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                            <strong>Test Case ${tc.test_case_number}</strong>
                            <span class="badge ${isPass ? 'bg-success' : 'bg-danger'}">${tc.status}</span>
                        </div>
                        <div class="font-monospace">Input: ${escapeHtml(tc.input)}</div>
                        <div class="font-monospace">Expected: ${escapeHtml(tc.expected)}</div>
                        <div class="font-monospace">Actual: ${escapeHtml(tc.actual)}</div>
                    </div>
                </div>
            `;
        });
        casesHtml += '</div>';

        outputConsole.innerHTML = headerHtml + casesHtml;
    }

    function setLoadingState(btn, isLoading, text) {
        if (isLoading) {
            btn.disabled = true;
            btn.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span> ${text}`;
        } else {
            btn.disabled = false;
            btn.innerHTML = text;
        }
    }
}

function escapeHtml(text) {
    if (!text) return '';
    const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
    return String(text).replace(/[&<>"']/g, m => map[m]);
}
