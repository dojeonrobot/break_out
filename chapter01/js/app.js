// 미션 및 힌트 데이터 정의
        const missions = [
            {
                id: 1, title: "MISSION 1", subtitle: "1번 도트매트릭스", imgSrc: "./images/001.png",
                hints: [
                    { pwd: "5656", imgSrc: "./images/007.png", unlocked: true, revealed: false },
                    { pwd: "4545", imgSrc: "./images/008.png", unlocked: false, revealed: false }
                ]
            },
            {
                id: 2, title: "MISSION 2", subtitle: "2번 도트매트릭스", imgSrc: "./images/002.png",
                hints: [
                    { pwd: "5656", imgSrc: "./images/009.png", unlocked: true, revealed: false },
                    { pwd: "4545", imgSrc: "./images/010.png", unlocked: false, revealed: false }
                ]
            },
            {
                id: 3, title: "MISSION 3", subtitle: "3번 도트매트릭스", imgSrc: "./images/003.png",
                hints: [
                    { pwd: "5656", imgSrc: "./images/011.png", unlocked: true, revealed: false },
                    { pwd: "4545", imgSrc: "./images/012.png", unlocked: false, revealed: false }
                ]
            },
            {
                id: 4, title: "MISSION 4", subtitle: "문자 변환표", imgSrc: "./images/004.png",
                hints: [
                    { pwd: "5656", imgSrc: "./images/013.png", unlocked: false, revealed: false }
                ]
            },
            {
                id: 5, title: "MISSION 5", subtitle: "기호 변환표", imgSrc: "./images/005.png",
                hints: [
                    { pwd: "4545", imgSrc: "./images/014.png", unlocked: false, revealed: false }
                ]
            }
        ];

        let currentMissionId = 1;
        let currentMode = 'mission';

        function init() {
            const tabsContainer = document.getElementById('tabs-container');
            
            missions.forEach(mission => {
                const button = document.createElement('button');
                button.id = `tab-btn-${mission.id}`;
                
                button.innerHTML = `
                    <div class="font-black text-xl mb-1">${mission.title}</div>
                    <div class="text-sm opacity-70">${mission.subtitle}</div>
                `;
                
                button.className = `tab-btn p-4 rounded-xl cursor-pointer ${mission.id === currentMissionId ? 'tab-active' : 'tab-inactive border border-gray-100'}`;
                button.onclick = () => loadMission(mission.id);
                
                tabsContainer.appendChild(button);
            });

            loadMission(1);
        }

        function loadMission(id) {
            currentMissionId = id;
            const mission = missions.find(m => m.id === id);

            missions.forEach(m => {
                const btn = document.getElementById(`tab-btn-${m.id}`);
                if (m.id === id) {
                    btn.classList.replace('tab-inactive', 'tab-active');
                    btn.classList.remove('border-gray-100');
                } else {
                    btn.classList.replace('tab-active', 'tab-inactive');
                    btn.classList.add('border-gray-100');
                }
            });

            document.getElementById('mission-title').innerText = mission.title;
            document.getElementById('mission-subtitle').innerText = mission.subtitle;
            
            const imgElement = document.getElementById('mission-image');
            const placeholderElement = document.getElementById('image-placeholder');
            const enlargeBtn = document.getElementById('enlarge-btn');
            
            if (mission.imgSrc) {
                imgElement.src = mission.imgSrc;
                imgElement.classList.remove('hidden');
                placeholderElement.classList.add('hidden');
                enlargeBtn.classList.remove('hidden');
            } else {
                imgElement.classList.add('hidden');
                placeholderElement.classList.remove('hidden');
                enlargeBtn.classList.add('hidden');
            }

            // 힌트 목록 다시 렌더링
            renderHints();
        }

        function renderHints() {
            const container = document.getElementById('hints-content');
            container.innerHTML = '';
            
            const mission = missions.find(m => m.id === currentMissionId);

            mission.hints.forEach((hint, index) => {
                const hintBox = document.createElement('div');
                hintBox.className = 'bg-white p-6 rounded-2xl border border-gray-200 shadow-sm flex flex-col gap-4 relative overflow-hidden flex-shrink-0';

                const titleLabel = document.createElement('span');
                titleLabel.className = 'text-base font-black text-[#22c55e] bg-green-100 w-max px-4 py-1.5 rounded-lg shadow-sm';
                titleLabel.innerText = `HINT 0${index + 1}`;
                hintBox.appendChild(titleLabel);

                if (hint.revealed) {
                    // 완전히 해제되어 이미지가 보이는 상태
                    const imgContainer = document.createElement('div');
                    imgContainer.className = 'relative mt-3 group cursor-pointer overflow-hidden rounded-xl';
                    
                    const hintImg = document.createElement('img');
                    hintImg.src = hint.imgSrc;
                    hintImg.alt = `힌트 이미지 ${index + 1}`;
                    hintImg.className = 'w-full max-h-[50vh] rounded-xl border border-gray-200 shadow-sm object-contain transition-transform duration-300 group-hover:scale-[1.02]';
                    
                    const enlargeBtn = document.createElement('button');
                    enlargeBtn.className = 'absolute top-4 right-4 bg-gray-900/80 hover:bg-[#22c55e] text-white px-4 py-2 rounded-xl text-base font-bold flex items-center gap-2 transition-opacity duration-300 opacity-0 group-hover:opacity-100 z-10 shadow-md';
                    enlargeBtn.innerHTML = '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7"></path></svg> 크게 보기';

                    // 클릭 시 전체화면
                    imgContainer.onclick = function() {
                        const modal = document.getElementById('image-modal');
                        const modalImg = document.getElementById('modal-image');
                        modalImg.src = hintImg.src;
                        modal.classList.remove('hidden');
                    };
                    
                    hintImg.onerror = function() {
                        imgContainer.outerHTML = `<div class="p-6 bg-red-50 text-red-500 rounded-xl text-lg font-bold text-center border border-red-200 shadow-sm mt-3">이미지를 불러올 수 없습니다.<br>(${hint.imgSrc})</div>`;
                    };

                    imgContainer.appendChild(hintImg);
                    imgContainer.appendChild(enlargeBtn);
                    hintBox.appendChild(imgContainer);
                    hintBox.classList.add('border-l-[6px]', 'border-l-[#4ade80]');

                } else if (hint.unlocked && !hint.revealed) {
                    // 비밀번호는 없지만, 아직 클릭해서 보지 않은 상태
                    const revealArea = document.createElement('div');
                    revealArea.className = 'flex flex-col items-center justify-center p-8 bg-[#f0fdf4] rounded-xl border-2 border-[#bbf7d0] border-dashed gap-3 mt-2 text-center';
                    
                    const icon = document.createElement('div');
                    icon.innerHTML = '🎁';
                    icon.className = 'text-5xl mb-2 hover:scale-110 transition-transform cursor-pointer';
                    icon.onclick = () => {
                        hint.revealed = true;
                        renderHints();
                    };
                    revealArea.appendChild(icon);

                    const helpText = document.createElement('div');
                    helpText.className = 'text-base text-[#166534] font-bold text-center';
                    helpText.innerHTML = '잠겨있지 않은 힌트입니다!<br>힌트를 바로 볼 수 있지만 조금 더 문제를 풀어보고 열람해주세요!';
                    revealArea.appendChild(helpText);

                    const btn = document.createElement('button');
                    btn.className = 'bg-[#4ade80] text-gray-900 text-lg font-black px-8 py-3 rounded-xl hover:bg-[#22c55e] transition-colors shadow-md mt-2';
                    btn.innerText = '클릭해서 힌트 보기';
                    btn.onclick = () => {
                        hint.revealed = true;
                        renderHints();
                    };

                    revealArea.appendChild(btn);
                    hintBox.appendChild(revealArea);
                    
                } else {
                    // 잠김: 비밀번호 입력란 표시
                    const lockArea = document.createElement('div');
                    lockArea.className = 'flex flex-col items-center justify-center p-8 bg-gray-50 rounded-xl border border-gray-200 border-dashed gap-3 mt-2';
                    
                    const icon = document.createElement('div');
                    icon.innerHTML = '🔒';
                    icon.className = 'text-4xl mb-2 opacity-50';
                    lockArea.appendChild(icon);

                    const helpText = document.createElement('span');
                    helpText.className = 'text-base text-gray-500 font-bold';
                    helpText.innerText = '비밀번호를 입력해 잠금을 해제하세요.';
                    lockArea.appendChild(helpText);

                    const inputGroup = document.createElement('div');
                    inputGroup.className = 'flex gap-3 w-full max-w-sm mt-2';

                    const input = document.createElement('input');
                    input.type = 'password';
                    input.placeholder = '비밀번호 입력';
                    input.className = 'flex-1 w-full bg-white border-2 border-gray-300 rounded-xl px-4 py-3 text-lg focus:outline-none focus:border-green-400 font-bold tracking-widest text-center transition-colors shadow-inner';
                    input.id = `hint-pwd-${index}`;
                    
                    input.addEventListener('keypress', function (e) {
                        if (e.key === 'Enter') unlockHint(index);
                    });

                    const btn = document.createElement('button');
                    btn.className = 'bg-gray-800 text-white text-base font-bold px-6 py-3 rounded-xl hover:bg-[#22c55e] transition-colors whitespace-nowrap shadow-md';
                    btn.innerText = '확인';
                    btn.onclick = () => unlockHint(index);

                    inputGroup.appendChild(input);
                    inputGroup.appendChild(btn);
                    lockArea.appendChild(inputGroup);
                    hintBox.appendChild(lockArea);
                }
                
                container.appendChild(hintBox);
            });
        }

        function unlockHint(index) {
            const mission = missions.find(m => m.id === currentMissionId);
            const input = document.getElementById(`hint-pwd-${index}`);
            const pwdValue = input.value.trim();
            
            // 선생님용 스텔스 만능키 'doro' 추가
            if (pwdValue === mission.hints[index].pwd || pwdValue === 'doro') {
                mission.hints[index].unlocked = true;
                mission.hints[index].revealed = true; // 잠금 해제와 동시에 이미지 표시
                renderHints(); 
            } else {
                alert('비밀번호가 일치하지 않습니다.');
                input.value = '';
                input.focus();
            }
        }

        function imageError() {
            const placeholderElement = document.getElementById('image-placeholder');
            const imgElement = document.getElementById('mission-image');
            const enlargeBtn = document.getElementById('enlarge-btn');

            imgElement.classList.add('hidden');
            enlargeBtn.classList.add('hidden'); 
            placeholderElement.classList.remove('hidden');
            
            const currentMission = missions.find(m => m.id === currentMissionId);
            placeholderElement.innerHTML = `
                <svg class="w-20 h-20 mx-auto mb-3 text-red-400 opacity-80" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                <p class="font-bold text-lg text-red-500 mb-2">이미지를 불러올 수 없습니다!</p>
                <p class="text-base text-gray-500">HTML 파일과 같은 폴더에<br><b class="text-gray-700">${currentMission.imgSrc.replace('./', '')}</b> 파일이 있는지 확인해주세요.</p>
            `;
        }

        function checkFinalAnswer() {
            const a1 = document.getElementById('ans1').value.trim().toUpperCase();
            const a2 = document.getElementById('ans2').value.trim().toUpperCase();
            const a3 = document.getElementById('ans3').value.trim().toUpperCase();
            const a4 = document.getElementById('ans4').value.trim().toUpperCase();

            if (!a1 || !a2 || !a3 || !a4) return;

            if (a1 === '4' && a2 === '+' && a3 === '10' && a4 === '14') {
                alert(`✨ 축하합니다! ✨\n\n마스터 키 [ 4, +, 10, 14 ]가 일치합니다.\n도로랜드 사파리의 시스템이 정상 복구되었습니다!`);
            } else {
                alert(`❌ 오류 ❌\n\n입력한 코드가 올바르지 않습니다.\n단서를 다시 확인해주세요.`);
                document.getElementById('ans1').value = '';
                document.getElementById('ans2').value = '';
                document.getElementById('ans3').value = '';
                document.getElementById('ans4').value = '';
                document.getElementById('ans1').focus();
            }
        }

        const inputs = [document.getElementById('ans1'), document.getElementById('ans2'), document.getElementById('ans3'), document.getElementById('ans4')];
        const maxLengths = [1, 1, 2, 2];
        
        inputs.forEach((input, index) => {
            input.addEventListener('input', function() {
                if(this.value.length === maxLengths[index]) {
                    if (index < 3) {
                        inputs[index + 1].focus();
                    } else {
                        setTimeout(checkFinalAnswer, 150);
                    }
                }
            });
            
            input.addEventListener('keydown', function(e) {
                if (e.key === 'Backspace' && this.value === '' && index > 0) {
                    inputs[index - 1].focus();
                }
                if (e.key === 'Enter') {
                    checkFinalAnswer();
                }
            });
        });

        // 우측 상단 탭 전환 함수
        function setMode(mode) {
            currentMode = mode;
            const btnMission = document.getElementById('btn-mode-mission');
            const btnHint = document.getElementById('btn-mode-hint');
            const missionContent = document.getElementById('mission-content');
            const hintsContent = document.getElementById('hints-content');

            if (mode === 'mission') {
                btnMission.classList.add('bg-white', 'text-[#22c55e]', 'shadow');
                btnMission.classList.remove('text-gray-500', 'hover:text-gray-700', 'hover:bg-gray-100');
                
                btnHint.classList.remove('bg-white', 'text-[#22c55e]', 'shadow');
                btnHint.classList.add('text-gray-500', 'hover:text-gray-700', 'hover:bg-gray-100');

                missionContent.classList.remove('hidden');
                missionContent.classList.add('flex');
                hintsContent.classList.add('hidden');
                hintsContent.classList.remove('flex');
            } else {
                btnHint.classList.add('bg-white', 'text-[#22c55e]', 'shadow');
                btnHint.classList.remove('text-gray-500', 'hover:text-gray-700', 'hover:bg-gray-100');
                
                btnMission.classList.remove('bg-white', 'text-[#22c55e]', 'shadow');
                btnMission.classList.add('text-gray-500', 'hover:text-gray-700', 'hover:bg-gray-100');

                hintsContent.classList.remove('hidden');
                hintsContent.classList.add('flex');
                missionContent.classList.add('hidden');
                missionContent.classList.remove('flex');
            }
        }

        function openModal() {
            const imgElement = document.getElementById('mission-image');
            if (imgElement.classList.contains('hidden')) return; 
            
            const modal = document.getElementById('image-modal');
            const modalImg = document.getElementById('modal-image');
            
            modalImg.src = imgElement.src;
            modal.classList.remove('hidden');
        }

        function closeModal() {
            document.getElementById('image-modal').classList.add('hidden');
        }

        function openDotModal() {
            document.getElementById('dot-modal').classList.remove('hidden');
            const msgBox = document.getElementById('dot-result-message');
            msgBox.classList.add('hidden');
            msgBox.innerHTML = '';
        }

        function closeDotModal() {
            document.getElementById('dot-modal').classList.add('hidden');
        }

        function checkDotModalAnswer() {
            const v1 = document.getElementById('dot-code-1').value.trim();
            const v2 = document.getElementById('dot-code-2').value.trim();
            const v3 = document.getElementById('dot-code-3').value.trim();
            const v4 = document.getElementById('dot-code-4').value.trim();
            const msgBox = document.getElementById('dot-result-message');

            if (v1 === '4' && v2 === '+' && v3 === '10' && v4 === '14') {
                msgBox.innerHTML = '✨ 정답입니다! 마스터 키는 [ 4, +, 10, 14 ] 입니다! ✨<br><span class="text-xl font-bold text-gray-600 mt-2 block">이제 직접 칠해본 도트 모양을 참고해서 <span class="text-[#c0392b] font-black">실제 코드</span>를 작성해 보세요! (우측 상단 X로 닫기)</span>';
                msgBox.className = 'text-2xl font-black mt-3 text-green-600 animate-bounce block text-center';

                document.getElementById('ans1').value = '4';
                document.getElementById('ans2').value = '+';
                document.getElementById('ans3').value = '10';
                document.getElementById('ans4').value = '14';
            } else {
                msgBox.innerHTML = '❌ 코드가 올바르지 않습니다. 다시 확인해보세요!';
                msgBox.className = 'text-xl font-bold mt-3 text-red-500 block animate-pulse text-center';
            }
        }

        function initDotGrids() {
            for (let g = 1; g <= 4; g++) {
                const gridContainer = document.getElementById(`grid-${g}`);
                if (!gridContainer) continue;
                gridContainer.innerHTML = ''; 
                
                for (let i = 0; i < 64; i++) {
                    const dot = document.createElement('div');
                    dot.className = 'bg-white rounded-full w-full h-full cursor-pointer transition-colors duration-150 shadow-sm';
                    dot.onclick = function() {
                        if (this.classList.contains('bg-white')) {
                            this.classList.replace('bg-white', 'bg-gray-900');
                        } else {
                            this.classList.replace('bg-gray-900', 'bg-white');
                        }
                    };
                    gridContainer.appendChild(dot);
                }
            }
        }

        window.onload = () => {
            init();
            initDotGrids();
        };