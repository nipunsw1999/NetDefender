
rule detect_specific_python_packages {
    strings:
        $pyfiglet = "pyfiglet"
        $h2o_wave = "h2o-wave==1.6.2"
        $h2ogpte = "h2ogpte==1.6.27"
        $google_genai = "google-generativeai"
        $langchain = "langchain"
        $langchain_groq = "langchain-groq"
        $langchain_google_genai = "langchain-google-genai"
        $python_dotenv = "python-dotenv"
    condition:
        any of them
}
