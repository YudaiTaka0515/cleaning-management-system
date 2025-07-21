"""
モバイル/タブレット対応の修正モジュール

iPadやモバイルデバイスでの表示問題を解決するための設定とスタイリング
"""

import streamlit as st


def apply_mobile_styles():
    """モバイル/タブレット対応のスタイルを適用"""

    # モバイル対応CSS
    mobile_css = """
    <style>
    /* メイン設定 */
    .main > div {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* モバイル/タブレット対応 */
    @media screen and (max-width: 1024px) {
        /* iPad Pro以下のサイズ */
        .main > div {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        
        /* メトリクス表示の調整 */
        [data-testid="metric-container"] {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
        }
        
        /* チャート表示の調整 */
        .js-plotly-plot {
            width: 100% !important;
        }
        
        /* サイドバーの調整 */
        .css-1d391kg {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        
        /* ボタンの調整（タッチに最適化） */
        .stButton > button {
            width: 100%;
            height: 3rem;
            font-size: 1.1rem;
            margin: 0.5rem 0;
        }
        
        /* テーブルの横スクロール対応 */
        .dataframe {
            font-size: 0.9rem;
        }
        
        /* プログレスバーの調整 */
        .stProgress {
            height: 2rem;
        }
    }
    
    @media screen and (max-width: 768px) {
        /* iPad mini以下のサイズ */
        .main > div {
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }
        
        /* フォントサイズの調整 */
        h1 { font-size: 1.5rem !important; }
        h2 { font-size: 1.3rem !important; }
        h3 { font-size: 1.1rem !important; }
        
        /* カラムの調整 */
        .row-widget.stRadio > div {
            flex-direction: column;
        }
        
        /* セレクトボックスの調整 */
        .stSelectbox > div > div {
            min-height: 3rem;
        }
    }
    
    /* タッチデバイス用の改善 */
    @media (hover: none) and (pointer: coarse) {
        /* タッチデバイスでのインタラクション改善 */
        .stButton > button:hover {
            background-color: #0066cc !important;
            color: white !important;
        }
        
        /* エクスパンダーの調整 */
        .streamlit-expanderHeader {
            padding: 1rem;
            font-size: 1.1rem;
        }
    }
    
    /* エラー表示の改善 */
    .stAlert {
        margin: 1rem 0;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    
    /* Plotlyチャートのレスポンシブ対応 */
    .js-plotly-plot .plotly .modebar {
        left: 0 !important;
        right: auto !important;
    }
    
    /* 読み込み中表示の改善 */
    .stSpinner > div {
        border: 3px solid #f3f3f3;
        border-top: 3px solid #3498db;
        border-radius: 50%;
        width: 40px;
        height: 40px;
    }
    </style>
    """

    st.markdown(mobile_css, unsafe_allow_html=True)


def add_error_handling_js():
    """エラーハンドリング用のJavaScriptを追加"""

    error_js = """
    <script>
    // エラーハンドリングの改善
    window.addEventListener('error', function(event) {
        console.log('JavaScript Error:', event.error);
        // Streamlitのエラーハンドリングに干渉しないよう、ログのみ
        return false;
    });
    
    // unhandled promise rejection のキャッチ
    window.addEventListener('unhandledrejection', function(event) {
        console.log('Unhandled Promise Rejection:', event.reason);
        // Streamlitのエラーハンドリングに干渉しないよう、ログのみ
    });
    
    // ビューポート設定の確認
    if (!document.querySelector('meta[name="viewport"]')) {
        const viewport = document.createElement('meta');
        viewport.name = 'viewport';
        viewport.content = 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no';
        document.head.appendChild(viewport);
    }
    
    // タッチイベントの最適化
    document.addEventListener('touchstart', function(){}, {passive: true});
    document.addEventListener('touchmove', function(){}, {passive: true});
    
    // iOS Safari特有の問題の対応
    if (/iPad|iPhone|iPod/.test(navigator.userAgent)) {
        // iOS Safariでの100vh問題の対応
        function setVh() {
            let vh = window.innerHeight * 0.01;
            document.documentElement.style.setProperty('--vh', vh + 'px');
        }
        setVh();
        window.addEventListener('resize', setVh);
        window.addEventListener('orientationchange', setVh);
    }
    
    // メモリ使用量の監視（開発用）
    if (typeof performance !== 'undefined' && performance.memory) {
        setInterval(() => {
            if (performance.memory.usedJSHeapSize > 100 * 1024 * 1024) { // 100MB
                console.warn('High memory usage detected:', 
                    Math.round(performance.memory.usedJSHeapSize / 1024 / 1024) + 'MB');
            }
        }, 30000); // 30秒ごと
    }
    </script>
    """

    st.markdown(error_js, unsafe_allow_html=True)


def check_device_compatibility():
    """デバイス互換性をチェックして警告表示"""

    compatibility_check = """
    <script>
    // デバイス情報の取得
    const userAgent = navigator.userAgent;
    const isIOS = /iPad|iPhone|iPod/.test(userAgent);
    const isAndroid = /Android/.test(userAgent);
    const isSafari = /Safari/.test(userAgent) && !/Chrome/.test(userAgent);
    
    // 古いブラウザの警告
    const isOldBrowser = !window.fetch || !window.Promise || !window.Map;
    
    if (isOldBrowser) {
        console.warn('古いブラウザが検出されました。一部機能が正常に動作しない可能性があります。');
    }
    
    // デバイス情報をコンソールに出力（デバッグ用）
    console.log('Device Info:', {
        userAgent: userAgent,
        isIOS: isIOS,
        isAndroid: isAndroid,
        isSafari: isSafari,
        screenSize: window.screen.width + 'x' + window.screen.height,
        viewport: window.innerWidth + 'x' + window.innerHeight
    });
    </script>
    """

    st.markdown(compatibility_check, unsafe_allow_html=True)


def apply_plotly_mobile_config():
    """Plotlyチャートのモバイル設定を返す"""

    mobile_config = {
        "displayModeBar": True,
        "displaylogo": False,
        "modeBarButtonsToRemove": [
            "pan2d",
            "lasso2d",
            "select2d",
            "autoScale2d",
            "hoverClosestCartesian",
            "hoverCompareCartesian",
        ],
        "responsive": True,
        "toImageButtonOptions": {
            "format": "png",
            "filename": "cleaning_chart",
            "height": 500,
            "width": 700,
            "scale": 1,
        },
    }

    return mobile_config
