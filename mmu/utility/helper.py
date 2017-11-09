# Helper class that defines useful formatting functions
class Helper:

    # Turns a greek name to all caps and without accents
    # @todo: Use regex or other way to speed up
    def normalize_greek_name(self, name):
        # α, β, γ, δ, ε, ζ, η, θ, ι, κ, λ, μ, ν, ξ, ο, π, ρ, σ, τ, υ, φ, χ, ψ, ω
        name = name.upper()
        replace_accents = {'Ά': 'Α', 'Έ': 'Ε', 'Ή': 'Η', 'Ί': 'Ι', 'Ϊ': 'Ι', 'Ό': 'Ο', 'Ύ': 'Υ', 'Ϋ': 'Υ', 'Ώ': 'Ω'}

        for accent in replace_accents:
            name =  name.replace(accent, replace_accents[accent])

        return name
