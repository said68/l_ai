import openai
import streamlit as st
import json
import gs
import prompts
import bp
import tc
import os

api_key = st.secrets["OPENAI_API_KEY"]


def log_to_file(log_message, filename="log.txt"):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    log_file_path = os.path.join(current_directory, filename)
    with open(log_file_path, "a") as log_file:
        log_file.write(log_message + "\n")


def load_settings():
    try:
        with open("settings.json", "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_settings(settings):
    with open("settings.json", "w") as file:
        json.dump(settings, file, indent=4)


settings = load_settings()

show_token_cost_default = settings.get("show_token_cost", False)
temperature_default = settings.get("temperature", 0.7)
top_p_default = settings.get("top_p", 1.0)
model_default = settings.get("model", "gpt-3.5-turbo")

st.sidebar.markdown("<span style='color: blue; font-weight: bold; font-size: 20px;'>Paramètres :</span>", unsafe_allow_html=True)

show_token_cost = True

temperature = st.sidebar.slider("Température", 0.1, 1.0, temperature_default)
top_p = st.sidebar.slider("Top P", 0.1, 1.0, top_p_default)
model = st.sidebar.selectbox(
    "Modèle",
    ["gpt-3.5-turbo", "gpt-3.5-turbo-16k"],
    index=0 if model_default == "gpt-3.5-turbo" else 1,
    )
st.sidebar.markdown("<span style='color: blue;'>**Des fonctions spéciales à cocher au besoin :**</span>", unsafe_allow_html=True)
activate_summary = st.sidebar.checkbox("Résumé d'une page URL")
activate_rewrite = st.sidebar.checkbox("Réécriture d'un texte en angalais")
activate_google = st.sidebar.checkbox("Recherche d'un sujet sur Google")

# Update settings with the new values
settings.update(
    {
        "show_token_cost": show_token_cost,
        "temperature": temperature,
        "top_p": top_p,
        "model": model,
    }
)
save_settings(settings)


# Initialisation ou récupération de l'état de la session
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'cumulative_tokens' not in st.session_state:
    st.session_state.cumulative_tokens = 0
if 'cumulative_cost' not in st.session_state:
    st.session_state.cumulative_cost = 0


st.title("ChatGPT L")


# Set the API key if it's provided
if api_key:
    openai.api_key = api_key
else:
    st.warning("Please provide a valid OpenAI API Key.")
    st.stop()


if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Comment puis-je vous aider?"):
    start_prompt_used = ""

    # Traitement des commandes spécifiques
    if activate_summary and (prompt.startswith("http://") or prompt.startswith("https://")):
        blog_url = prompt
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Résumer : " + blog_url)
            blog_summary_prompt = bp.get_blog_summary_prompt(blog_url)
            response_obj = openai.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": blog_summary_prompt}],
                temperature=temperature,
                top_p=top_p,
                stream=True,
            )
            blog_summary = ""

                
            for response in response_obj:
                if response.choices[0].delta.content is not None:
                    blog_summary += response.choices[0].delta.content
                message_placeholder.markdown(blog_summary + "▌")

            # update the whole prompt to update token count
            start_prompt_used = blog_summary_prompt + blog_summary

            message_placeholder.markdown(blog_summary)  # Display the summary in chat
            st.session_state.messages.append(
                {"role": "assistant", "content": blog_summary}
            )

    elif activate_rewrite:
        input_text = prompt.split(" ", 1)[1].strip()
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Réécriture...")
            rewrite_prompt = prompts.rewrite_prompt.format(text=input_text)
            response_obj = openai.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": rewrite_prompt}],
                temperature=temperature,
                top_p=top_p,
                stream=True,
            )
            new_written_text = ""
            for response in response_obj:
                if response.choices[0].delta.content is not None:
                    new_written_text += response.choices[0].delta.content
                message_placeholder.markdown(new_written_text + "▌")

            # update the whole prompt to update token count
            start_prompt_used = rewrite_prompt + new_written_text

            message_placeholder.markdown(new_written_text)
            st.session_state.messages.append(
                {"role": "assistant", "content": new_written_text}
            )

    elif activate_google:
        input_query = prompt.split(" ", 1)[1].strip()
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown(
                "Recherche Google pour : " + input_query + " ..."
            )
            search_results = gs.search_google_web_automation(input_query)
            over_all_summary = ""

            source_links = "\n \n Sources: \n \n"

            for result in search_results:
                blog_url = result["url"]
                source_links += blog_url + "\n \n"
                message_placeholder.markdown(f"Recherche terminée, lecture {blog_url}")
                blog_summary_prompt = bp.get_blog_summary_prompt(blog_url)
                response_obj = openai.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": blog_summary_prompt}],
                    temperature=temperature,
                    top_p=top_p,
                    stream=True,
                )

                blog_summary = ""
                for response in response_obj:
                    if response.choices[0].delta.content is not None:
                        blog_summary += response.choices[0].delta.content

                over_all_summary = over_all_summary + blog_summary
                start_prompt_used = blog_summary_prompt + blog_summary

            message_placeholder.markdown(f"Génération finale du rapport de recherche...")

            new_search_prompt = prompts.google_search_prompt.format(
                input=over_all_summary
            )

            response_obj = openai.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": new_search_prompt}],
                temperature=temperature,
                top_p=top_p,
                stream=True,
            )
            research_final = ""
            for response in response_obj:
                if response.choices[0].delta.content is not None:
                    research_final += response.choices[0].delta.content
                message_placeholder.markdown(research_final + "▌")

            start_prompt_used = start_prompt_used + new_search_prompt + research_final

            message_placeholder.markdown(research_final + source_links)
            st.session_state.messages.append(
                {"role": "assistant", "content": research_final + source_links}
            )

    else:
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            response_obj = openai.chat.completions.create(
                model=model,
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
                temperature=temperature,
                top_p=top_p,
            )

            for response in response_obj:
                if response.choices[0].delta.content is not None:
                    full_response += response.choices[0].delta.content
                message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

            start_prompt_used = prompt + full_response

            st.session_state.messages.append(
                {"role": "assistant", "content": full_response}
            )

    # Gestion des coûts des tokens si activée
    if show_token_cost:
        total_tokens_used = tc.count_tokens(start_prompt_used, model)
        total_cost = tc.estimate_input_cost_optimized(
            model, total_tokens_used
        )
        st.session_state.cumulative_tokens += total_tokens_used
        st.session_state.cumulative_cost += total_cost

        # Redisplay the updated cumulative tokens and cost in the left sidebar
        st.sidebar.markdown(
            f"**Total des 'tokens' utilisés cette session :** {st.session_state.cumulative_tokens}"
        )
        st.sidebar.markdown(
            f"**Coût total de cette session :** ${st.session_state.cumulative_cost:.6f}"
        )
