document.addEventListener('DOMContentLoaded', function () {
    const chatContainer = document.getElementById('chatContainer');
    const userInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');
    const clearBtn = document.getElementById('clearChat');
    const topKSlider = document.getElementById('top_k_slider');
    const topKValueDisplay = document.getElementById('top_k_value');

    let currentTopK = parseInt(topKSlider.value) || 5;

    topKSlider.addEventListener('input', function () {
        currentTopK = parseInt(this.value);
        topKValueDisplay.textContent = currentTopK;
    });

    function markdownToHtml(text) {
        if (typeof text !== 'string') return text;

        text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
        text = text.replace(/`(.*?)`/g, '<code>$1</code>');
        text = text.replace(/^\s*\*\s+(.*)$/gm, '<li>$1</li>');
        if (text.includes('<li>')) {
            text = text.replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>');
        }
        text = text.replace(/\n/g, '<br>');
        return text;
    }

    function addMessage(role, content, isStreaming = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `flex ${role === 'user' ? 'justify-end' : 'justify-start'} mb-4 animate-fadeIn`;

        if (role === 'assistant' && !isStreaming) {
            messageDiv.innerHTML = `
            <div class="max-w-[85%] flex gap-3">
                <div class="w-9 h-9 rounded-full bg-gradient-to-br from-iran-green to-green-600 flex items-center justify-center text-white">🤖</div>
                <div class="bg-white border border-gray-200 p-4 rounded-2xl rounded-bl-none shadow-sm break-words">
                    <strong class="text-iran-green block mb-1">یارا</strong>
                    ${simpleMarkdownToHtml(content)}
                </div>
            </div>
        `;
        } else if (role === 'user') {
            messageDiv.innerHTML = `
            <div class="max-w-[85%] flex gap-3">
                <div class="bg-blue-500 text-white p-4 rounded-2xl rounded-br-none shadow-sm break-words">
                    ${simpleMarkdownToHtml(content)}
                </div>
                <div class="w-9 h-9 rounded-full bg-blue-600 flex items-center justify-center text-white">👤</div>
            </div>
        `;
        } else {
            messageDiv.innerHTML = `
            <div class="max-w-[85%] flex gap-3">
                <div class="w-9 h-9 rounded-full bg-gradient-to-br from-iran-green to-green-600 flex items-center justify-center text-white">🤖</div>
                <div class="bg-white border border-gray-200 p-4 rounded-2xl rounded-bl-none shadow-sm break-words">
                    <strong class="text-iran-green block mb-1">یارا</strong>
                    ${content}
                </div>
            </div>
        `;
        }

        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    function addTypingIndicator() {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chat-message assistant-message';
        messageDiv.id = 'typingPlaceholder';

        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'avatar';
        avatarDiv.textContent = '🤖';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.innerHTML = `<strong>یارا:</strong> <span class="typing-dots">در حال پاسخ‌دهی...</span>`;

        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    function updateTypingContent(text) {
        const placeholder = document.getElementById('typingPlaceholder');
        if (placeholder) {
            // ✅ تبدیل Markdown به HTML حتی در حالت استریم
            placeholder.querySelector('.message-content').innerHTML = `<strong>یارا:</strong> ${markdownToHtml(text)}`;
        }
    }

    function removeTypingIndicator() {
        const placeholder = document.getElementById('typingPlaceholder');
        if (placeholder) placeholder.remove();
    }

    function displayChunks(chunks) {
        const existingSection = document.querySelector('.chunks-section');
        if (existingSection) existingSection.remove();

        if (!chunks || chunks.length === 0) return;

        const section = document.createElement('div');
        section.className = 'chunks-section';

        // ✅ جعبه توضیحی با Markdown
        const explanation = document.createElement('div');
        explanation.className = 'explanation-box';
        explanation.innerHTML = `
            <p>🧠 <strong>پاسخ من بر اساس این اسناد تولید شده:</strong></p>
            <ul>
                ${chunks.map((chunk, i) => {
            const source = chunk.metadata?.source || 'نامشخص';
            const page = chunk.metadata?.page || '?';
            const score = chunk.metadata?.score?.toFixed(2) || 'N/A';
            return `<li>📄 <strong>${source}</strong> (صفحه ${page}) — امتیاز: ${score}</li>`;
        }).join('')}
            </ul>
        `;
        section.appendChild(explanation);

        // ✅ جزئیات چانک‌ها با Markdown
        const detailsHeader = document.createElement('h4');
        detailsHeader.textContent = '📄 محتوای کامل اسناد مرتبط:';
        section.appendChild(detailsHeader);

        chunks.forEach(chunk => {
            const card = document.createElement('div');
            card.className = 'chunk-card';

            const score = chunk.metadata?.score !== undefined ? chunk.metadata.score.toFixed(2) : 'N/A';
            const source = chunk.metadata?.source || 'نامشخص';
            const page = chunk.metadata?.page || 'نامشخص';

            // ✅ تبدیل Markdown در محتوای چانک‌ها
            card.innerHTML = `
                <div class="chunk-meta">
                    <span class="chunk-score">امتیاز شباهت: ${score}</span>
                    <span class="source-tag">📄 منبع: ${source}</span>
                    <span class="source-tag">📄 صفحه: ${page}</span>
                </div>
                <div class="chunk-content">${markdownToHtml(truncateText(chunk.page_content, 400))}</div>
            `;
            section.appendChild(card);
        });

        chatContainer.insertAdjacentElement('afterend', section);
    }

    function truncateText(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.slice(0, maxLength) + '...';
    }

    async function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;

        addMessage('user', message);
        userInput.value = '';
        addTypingIndicator();

        try {
            const response = await fetch('/send_message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    top_k: currentTopK
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder('utf-8');
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });

                let boundary = buffer.indexOf('\n\n');
                while (boundary !== -1) {
                    let line = buffer.slice(0, boundary).trim();
                    buffer = buffer.slice(boundary + 2);

                    if (line.startsWith('data: ')) {
                        try {
                            const jsonStr = line.slice(6); // remove "data: "
                            const data = JSON.parse(jsonStr);

                            if (data.type === 'stream') {
                                updateTypingContent(data.content);
                            } else if (data.type === 'final') {
                                removeTypingIndicator();
                                addMessage('assistant', data.content);
                            } else if (data.type === 'chunks') {
                                displayChunks(data.content);
                            }
                        } catch (e) {
                            console.error("JSON parse error:", e);
                        }
                    }

                    boundary = buffer.indexOf('\n\n');
                }
            }

        } catch (error) {
            console.error("Fetch error:", error);
            removeTypingIndicator();
            addMessage('assistant', "❌ خطایی در ارتباط با سرور رخ داد. لطفاً دوباره تلاش کنید.");
        }
    }

    sendBtn.addEventListener('click', sendMessage);

    userInput.addEventListener('keypress', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    clearBtn.addEventListener('click', async function () {
        try {
            const response = await fetch('/clear_chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            if (response.ok) {
                chatContainer.innerHTML = '';
                const existingSection = document.querySelector('.chunks-section');
                if (existingSection) existingSection.remove();

                addMessage('assistant', "سلام! 😊 من یارا هستم — دستیار هوشمند شما. چطور می‌تونم کمکتون کنم؟");
            } else {
                alert("خطا در پاک‌کردن گفتگو");
            }
        } catch (e) {
            console.error("Clear chat error:", e);
            alert("اتصال به سرور برقرار نشد");
        }
    });
});